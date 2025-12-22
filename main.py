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

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()
app = FastAPI(title="SmartCargo-AIPA Backend")

ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "secret123")
FRONTEND_URL = "https://smartcargo-advisory.onrender.com"
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")
SENDER_EMAIL = "reports@smartcargo-advisory.com"

# --- BASE DE DATOS ---
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
    status = Column(String)

Base.metadata.create_all(bind=engine)

# --- MODELOS DE DATOS ---
class CargoInput(BaseModel):
    awb: str
    content: str
    height_cm: float
    weight_declared: float
    packing_integrity: str
    ispm15_seal: str
    dg_type: str
    weight_match: str
    email: Optional[str] = None # Capturamos el email aquí

class AdvisoryRequest(BaseModel):
    prompt: str

# --- FUNCIONES AUXILIARES ---
def save_audit(awb: str, score: int, alerts: list, status: str):
    db = SessionLocal()
    record = AuditRecord(awb=awb, risk_score=score, alerts=alerts, status=status)
    db.add(record)
    db.commit()
    db.close()

async def send_confirmation_email(customer_email: str, awb: str, risk_score: int):
    if not EMAIL_API_KEY:
        return
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {"Authorization": f"Bearer {EMAIL_API_KEY}"}
    data = {
        "personalizations": [{"to": [{"email": customer_email}]}],
        "from": {"email": SENDER_EMAIL},
        "subject": f"Resumen de Auditoría AIPA - AWB: {awb}",
        "content": [{"type": "text/plain", "value": f"Auditoría AWB {awb} completada: {risk_score}% de riesgo."}]
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data, headers=headers)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GEMINI IA ---
client_gemini = None
if os.getenv("GEMINI_API_KEY"):
    client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- ENDPOINTS ---
@app.post("/cargas")
async def validate_cargo_endpoint(cargo: CargoInput):
    alerts = []
    if cargo.ispm15_seal == "NO": alerts.append("ISPM-15 missing")
    if cargo.height_cm > 180: alerts.append("Height exceeds ULD limit")
    if cargo.packing_integrity == "CRITICAL": alerts.append("Critical packaging integrity")
    if cargo.weight_match == "NO": alerts.append("Weight mismatch")
    
    risk_score = min(len(alerts) * 25, 99)
    
    if cargo.email:
        await send_confirmation_email(cargo.email, cargo.awb, risk_score)
        
    return {"awb": cargo.awb, "alerts": alerts, "alertaScore": risk_score}

@app.post("/advisory")
async def advisory(request: AdvisoryRequest):
    if not client_gemini: raise HTTPException(status_code=503, detail="IA no configurada")
    try:
        response = client_gemini.models.generate_content(
            model="gemini-2.0-flash", # Actualizado a versión estable
            contents=[request.prompt],
            config=types.GenerateContentConfig(system_instruction="Expert logistics advisor. Concise.")
        )
        return {"data": response.text}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    description: str = Form(...),
    awb: Optional[str] = Form(None),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    if user == ADMIN_USER and password == ADMIN_PASS:
        save_audit(awb=awb or "ADMIN", score=0, alerts=[], status="ADMIN_BYPASS")
        return {"url": f"{FRONTEND_URL}/success.html?access=granted"}

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
        return {"url": session.url}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/history")
async def get_audit_history(user: str, password: str):
    if user != ADMIN_USER or password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="No autorizado")
    db = SessionLocal()
    records = db.query(AuditRecord).order_by(AuditRecord.id.desc()).limit(50).all()
    db.close()
    return records

@app.get("/")
def health(): return {"status": "AIPA Operational"}
