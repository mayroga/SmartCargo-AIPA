import os
import stripe
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

# --- CONFIGURACIÓN ---
load_dotenv()
app = FastAPI(title="SmartCargo-AIPA Backend")

ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "secret123")
FRONTEND_URL = "https://smartcargo-advisory.onrender.com"
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

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
    status = Column(String) # 'PAID' o 'ADMIN_BYPASS'

Base.metadata.create_all(bind=engine)

def save_audit(awb: str, score: int, alerts: list, status: str):
    db = SessionLocal()
    record = AuditRecord(awb=awb, risk_score=score, alerts=alerts, status=status)
    db.add(record)
    db.commit()
    db.close()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GEMINI ---
client = None
try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        client = genai.Client(api_key=gemini_key)
except Exception as e:
    print(f"Gemini Error: {e}")

# --- MODELOS ---
class CargoInput(BaseModel):
    awb: str
    content: str
    height_cm: float
    weight_declared: float
    packing_integrity: str
    ispm15_seal: str
    dg_type: str
    weight_match: str

class AdvisoryRequest(BaseModel):
    prompt: str

# --- ENDPOINTS ---

@app.post("/cargas")
async def validate_cargo_endpoint(cargo: CargoInput):
    alerts = []
    if cargo.ispm15_seal == "NO": alerts.append("ISPM-15 missing")
    if cargo.height_cm > 180: alerts.append("Height exceeds ULD limit")
    if cargo.packing_integrity == "CRITICAL": alerts.append("Critical packaging integrity")
    if cargo.weight_match == "NO": alerts.append("Weight mismatch")
    
    risk_score = min(len(alerts) * 25, 99)
    return {"awb": cargo.awb, "alerts": alerts, "alertaScore": risk_score}

@app.post("/advisory")
async def advisory(request: AdvisoryRequest):
    if not client: raise HTTPException(status_code=503, detail="IA no configurada")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[request.prompt],
            config=types.GenerateContentConfig(system_instruction="Expert logistics advisor. Concise solutions.")
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

@app.get("/")
def health(): return {"status": "AIPA Operational"}
# -----------------------------------------------------
# CONSULTA DE HISTORIAL (SOLO ADMIN)
# -----------------------------------------------------
@app.get("/admin/history")
async def get_audit_history(user: str, password: str):
    # Validar que sea el administrador quien consulta
    if user != ADMIN_USER or password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="No autorizado")

    db = SessionLocal()
    try:
        # Traer las últimas 50 auditorías
        records = db.query(AuditRecord).order_by(AuditRecord.id.desc()).limit(50).all()
        return records
    finally:
        db.close()
