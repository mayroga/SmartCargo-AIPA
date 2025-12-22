import os
import stripe
import httpx
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# =====================================================
# 1. CARGA DE CONFIGURACIÓN
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
# 2. CONFIGURACIÓN DE BASE DE DATOS (SOLUCIÓN AL ERROR)
# =====================================================
DATABASE_URL = os.getenv("DATABASE_URL")

# Si la URL no existe (Error None), usamos SQLite para evitar que la app falle
if not DATABASE_URL:
    print("WARNING: DATABASE_URL no encontrada. Usando SQLite temporal.")
    DATABASE_URL = "sqlite:///./test.db"
else:
    # Render entrega postgres://, SQLAlchemy requiere postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditRecord(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    awb = Column(String)
    risk_score = Column(Integer)
    alerts = Column(JSON)
    status = Column(String)

# Crear tablas
Base.metadata.create_all(bind=engine)

# =====================================================
# 3. MODELOS Y LOGICA DE NEGOCIO
# =====================================================
class CargoInput(BaseModel):
    awb: str
    content: str
    height_cm: float
    weight_declared: float
    packing_integrity: str
    ispm15_seal: str
    dg_type: str 
    weight_match: str
    email: Optional[str] = None

class AdvisoryRequest(BaseModel):
    prompt: str

def save_audit(awb: str, score: int, alerts: list, status: str):
    db = SessionLocal()
    try:
        record = AuditRecord(awb=awb, risk_score=score, alerts=alerts, status=status)
        db.add(record)
        db.commit()
    finally:
        db.close()

async def send_confirmation_email(customer_email: str, awb: str, risk_score: int):
    if not EMAIL_API_KEY: return
    disclaimer = "\n\n--- AVISO LEGAL ---\nReporte consultivo basado en IA. No sustituye inspección física."
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {"Authorization": f"Bearer {EMAIL_API_KEY}"}
    data = {
        "personalizations": [{"to": [{"email": customer_email}]}],
        "from": {"email": SENDER_EMAIL},
        "subject": f"Auditoría AIPA Completada - AWB: {awb}",
        "content": [{"type": "text/plain", "value": f"Su reporte para el AWB {awb} indica un {risk_score}% de riesgo.{disclaimer}"}]
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data, headers=headers)

# =====================================================
# 4. IA Y SEGURIDAD LEGAL
# =====================================================
client_gemini = None
if os.getenv("GEMINI_API_KEY"):
    client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

system_instruction = (
    "Eres SMARTCARGO CONSULTING. Experto en IATA DGR, PER y LAR. "
    "IMPORTANTE: Siempre incluye: 'Verifique con el manual oficial y la aerolínea'. "
    "Tu objetivo es prevenir el rechazo de carga en almacén (Warehouse Rejection)."
)

# =====================================================
# 5. ENDPOINTS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/cargas")
async def validate_cargo_endpoint(cargo: CargoInput):
    alerts = []
    risk_score = 0

    # Lógica Analista de Riesgos
    if cargo.ispm15_seal == "NO":
        alerts.append("R001: Falta sello ISPM-15 (Embalaje de madera)")
        risk_score += 25
    if cargo.height_cm > 180:
        alerts.append("R002: Altura excede límite ULD estándar")
        risk_score += 20
    if cargo.packing_integrity == "CRITICAL":
        alerts.append("R003: Embalaje dañado - Alto riesgo de rechazo")
        risk_score += 50
    
    # Detección Especializada
    if cargo.dg_type == "DANGEROUS":
        alerts.append("R009: Mercancía Peligrosa - Requiere Shipper's Declaration")
        risk_score += 30
    if "lithium" in cargo.content.lower():
        alerts.append("R015: Baterías de Litio - Revisar IATA PI 965")
        risk_score += 40

    risk_score = min(risk_score, 100)
    if cargo.email: await send_confirmation_email(cargo.email, cargo.awb, risk_score)
    
    return {"awb": cargo.awb, "alerts": alerts, "alertaScore": risk_score}

@app.post("/advisory")
async def advisory(request: AdvisoryRequest):
    if not client_gemini: raise HTTPException(status_code=503, detail="IA no configurada")
    response = client_gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=[request.prompt],
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return {"data": response.text}

@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    description: str = Form(...),
    awb: Optional[str] = Form(None),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # Bypass Admin
    if user == ADMIN_USER and password == ADMIN_PASS:
        save_audit(awb=awb or "ADMIN", score=0, alerts=[], status="ADMIN_BYPASS")
        return {"url": f"{FRONTEND_URL}/success.html?access=granted&awb={awb}"}

    # Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": description}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"{FRONTEND_URL}/success.html?session_id={{CHECKOUT_SESSION_ID}}&awb={awb}",
        cancel_url=f"{FRONTEND_URL}/cancel.html",
    )
    return {"url": session.url}

@app.get("/admin/history")
async def get_audit_history(user: str, password: str):
    if user != ADMIN_USER or password != ADMIN_PASS: raise HTTPException(status_code=401)
    db = SessionLocal()
    records = db.query(AuditRecord).order_by(AuditRecord.id.desc()).limit(50).all()
    db.close()
    return records

@app.get("/")
def health(): return {"status": "Operational", "db": "Connected"}
