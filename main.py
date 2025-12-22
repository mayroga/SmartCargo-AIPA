import os
import stripe
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

# =====================================================
# CARGA DE VARIABLES DE ENTORNO
# =====================================================
load_dotenv()

# =====================================================
# APP
# =====================================================
app = FastAPI(title="SmartCargo-AIPA Backend")

# =====================================================
# VARIABLES DE ENTORNO
# =====================================================
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "secret123")

FRONTEND_URL = "https://smartcargo-advisory.onrender.com"
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# =====================================================
# CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# GEMINI (ADVISOR IA)
# =====================================================
client = None
try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        client = genai.Client(api_key=gemini_key)
except Exception as e:
    print(f"WARNING: Gemini not initialized: {e}")

# =====================================================
# MODELOS
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


class AdvisoryRequest(BaseModel):
    prompt: str


# =====================================================
# MOTOR DE REGLAS AIPA (SIMPLIFICADO)
# =====================================================
ALERTS_DB = {
    "R001": "ISPM-15 missing – Pallet will be rejected",
    "R002": "Height exceeds standard ULD limit",
    "R003": "Critical packaging integrity – Immediate rejection",
    "R006": "Declared weight mismatch – Risk of HOLD",
}

def validate_cargo(cargo: CargoInput):
    alerts = []

    if cargo.ispm15_seal == "NO":
        alerts.append("R001")

    if cargo.height_cm > 180:
        alerts.append("R002")

    if cargo.packing_integrity == "CRITICAL":
        alerts.append("R003")

    if cargo.weight_match == "NO":
        alerts.append("R006")

    risk_score = min(len(alerts) * 25, 99)

    return {
        "awb": cargo.awb,
        "alerts": alerts,
        "alertaScore": risk_score
    }
from sqlalchemy import create_engine, Column, String, Float, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURACIÓN DE BASE DE DATOS ---
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

# Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

# Función para guardar
def save_audit(awb: str, score: int, alerts: list, status: str):
    db = SessionLocal()
    record = AuditRecord(awb=awb, risk_score=score, alerts=alerts, status=status)
    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()
# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/")
def health_check():
    return {"status": "AIPA Operational"}

# -----------------------------------------------------
# VALIDACIÓN DE CARGA
# -----------------------------------------------------
@app.post("/cargas")
async def validate_cargo_endpoint(cargo: CargoInput):
    return validate_cargo(cargo)

# -----------------------------------------------------
# ASESOR IA
# -----------------------------------------------------
@app.post("/advisory")
async def advisory(request: AdvisoryRequest):
    if not client:
        raise HTTPException(status_code=503, detail="Gemini not configured")

    system_instruction = (
        "You are SMARTCARGO CONSULTING, a preventive logistics advisor. "
        "Provide direct, corrective, regulation-based solutions (IATA, TSA, ISPM-15). "
        "Be concise and solution-first."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[request.prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return {"data": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------
# STRIPE + BYPASS ADMIN
# -----------------------------------------------------
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    description: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # BYPASS ADMIN
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {
            "url": f"{FRONTEND_URL}/success.html?access=granted",
            "message": "Admin bypass activated"
        }

    # STRIPE PAYMENT
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": description},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{FRONTEND_URL}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/cancel.html",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
