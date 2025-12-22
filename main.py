import os
import stripe
import httpx
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy import create_engine, Column, String, Float, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# =====================================================
# CONFIGURACIÓN Y VARIABLES DE ENTORNO
# =====================================================
load_dotenv()
app = FastAPI(title="SmartCargo-AIPA Professional Analyst")

ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "secret123")
FRONTEND_URL = "https://smartcargo-advisory.onrender.com"
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")
SENDER_EMAIL = "reports@smartcargo-advisory.com"

# =====================================================
# BASE DE DATOS (AUDITORÍA Y PERSISTENCIA)
# =====================================================
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditRecord(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    awb = Column(String)
    risk_score = Column(Integer)
    alerts = Column(JSON)
    status = Column(String) # 'PAID' o 'ADMIN_BYPASS'

Base.metadata.create_all(bind=engine)

# =====================================================
# MODELOS DE DATOS (Pydantic)
# =====================================================
class CargoInput(BaseModel):
    awb: str
    content: str
    height_cm: float
    weight_declared: float
    packing_integrity: str
    ispm15_seal: str
    dg_type: str  # NONE, DANGEROUS, PERISHABLE, LIVE_ANIMALS
    weight_match: str
    email: Optional[str] = None

class AdvisoryRequest(BaseModel):
    prompt: str

# =====================================================
# FUNCIONES AUXILIARES (Email, DB, Reglas)
# =====================================================
def save_audit(awb: str, score: int, alerts: list, status: str):
    db = SessionLocal()
    record = AuditRecord(awb=awb, risk_score=score, alerts=alerts, status=status)
    db.add(record)
    db.commit()
    db.close()

async def send_confirmation_email(customer_email: str, awb: str, risk_score: int):
    if not EMAIL_API_KEY: return
    
    disclaimer = ("\n\n--- AVISO LEGAL ---\n"
                  "Esta auditoría es consultiva basada en IA. No sustituye la inspección física obligatoria. "
                  "SmartCargo no se hace responsable por retenciones, multas o daños.")
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {"Authorization": f"Bearer {EMAIL_API_KEY}"}
    data = {
        "personalizations": [{"to": [{"email": customer_email}]}],
        "from": {"email": SENDER_EMAIL},
        "subject": f"Auditoría AIPA Completada - AWB: {awb}",
        "content": [{"type": "text/plain", "value": f"Su reporte para el AWB {awb} indica un {risk_score}% de riesgo de rechazo.{disclaimer}"}]
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data, headers=headers)

# =====================================================
# CONFIGURACIÓN DE IA (Analista Experto IATA)
# =====================================================
client_gemini = None
if os.getenv("GEMINI_API_KEY"):
    client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

system_instruction = (
    "Eres SMARTCARGO CONSULTING, experto en manuales IATA DGR, PER y LAR. "
    "Tu enfoque es preventivo para evitar el 'Warehouse Rejection'. "
    "IMPORTANTE: Todas tus recomendaciones DEBEN incluir: 'Verifique siempre con el manual oficial vigente y su aerolínea'. "
    "Cita normativas brevemente (ej. PI 965) y sé directo."
)

# =====================================================
# ENDPOINTS
# =====================================================

# --- 1. MOTOR ANALISTA DE RIESGOS ---
@app.post("/cargas")
async def validate_cargo_endpoint(cargo: CargoInput):
    alerts = []
    risk_score = 0

    # Reglas Físicas
    if cargo.ispm15_seal == "NO":
        alerts.append("R001: Falta sello ISPM-15 - Riesgo de rechazo fitosanitario")
        risk_score += 25
    if cargo.height_cm > 180:
        alerts.append("R002: Altura excede límite estándar ULD (160-180cm)")
        risk_score += 20
    if cargo.packing_integrity == "CRITICAL":
        alerts.append("R003: Embalaje dañado - Rechazo inmediato por seguridad")
        risk_score += 50
    if cargo.weight_match == "NO":
        alerts.append("R006: Discrepancia de peso - Riesgo de pesaje obligatorio y demora")
        risk_score += 15

    # Reglas Técnicas Especializadas
    if cargo.dg_type == "DANGEROUS":
        alerts.append("R009: Mercancía Peligrosa - Requiere Shipper's Declaration y etiquetas de clase")
        risk_score += 30
    
    if "lithium" in cargo.content.lower() or "battery" in cargo.content.lower():
        alerts.append("R015: Baterías de Litio - Cumplir con IATA PI 965-970 obligatoriamente")
        risk_score += 40

    if cargo.dg_type == "PERISHABLE" or any(x in cargo.content.lower() for x in ["fish", "fresh", "meat", "fruit"]):
        alerts.append("R012: Perecederos - Verificar etiquetas 'Perishable' y control de temperatura")
        risk_score += 25

    risk_score = min(risk_score, 100)

    if cargo.email:
        await send_confirmation_email(cargo.email, cargo.awb, risk_score)
        
    return {"awb": cargo.awb, "alerts": alerts, "alertaScore": risk_score}

# --- 2. ASESOR IA (CONSULTORÍA) ---
@app.post("/advisory")
async def advisory(request: AdvisoryRequest):
    if not client_gemini: raise HTTPException(status_code=503, detail="IA no configurada")
    try:
        response = client_gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=[request.prompt],
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        return {"data": response.text}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- 3. PAGOS Y BYPASS ---
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    description: str = Form(...),
    awb: Optional[str] = Form(None),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # Bypass Admin con registro
    if user == ADMIN_USER and password == ADMIN_PASS:
        save_audit(awb=awb or "ADMIN_TASK", score=0, alerts=[], status="ADMIN_BYPASS")
        return {"url": f"{FRONTEND_URL}/success.html?access=granted&awb={awb}"}

    # Proceso Stripe
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {"currency": "usd", "product_data": {"name": description}, "unit_amount": int(amount * 100)},
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{FRONTEND_URL}/success.html?session_id={{CHECKOUT_SESSION_ID}}&awb={awb}",
            cancel_url=f"{FRONTEND_URL}/cancel.html",
        )
        # Nota: El registro 'PAID' se recomienda hacer vía Webhook de Stripe para mayor seguridad
        return {"url": session.url}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- 4. ADMINISTRACIÓN ---
@app.get("/admin/history")
async def get_audit_history(user: str, password: str):
    if user != ADMIN_USER or password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="No autorizado")
    db = SessionLocal()
    records = db.query(AuditRecord).order_by(AuditRecord.id.desc()).limit(50).all()
    db.close()
    return records

# --- 5. HEALTH CHECK ---
@app.get("/")
def health(): return {"status": "AIPA Operational", "version": "2.0-Professional"}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
