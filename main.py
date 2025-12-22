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
# 2. MOTOR DE BASE DE DATOS (CORRECCIÓN DE PARSING)
# =====================================================
def get_db_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        return "sqlite:///./test.db"
    
    # IMPORTANTE: SQLAlchemy 1.4+ requiere 'postgresql://' no 'postgres://'
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # Eliminar espacios en blanco accidentales
    return url.strip()

try:
    engine = create_engine(get_db_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"Error fatal configurando el motor de DB: {e}")
    # Fallback extremo para que la app no muera en el despliegue
    engine = create_engine("sqlite:///./backup.db")
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

# =====================================================
# 3. MODELOS Y LÓGICA
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
    except Exception as e:
        print(f"Error guardando auditoría: {e}")
    finally:
        db.close()

# =====================================================
# 4. IA Y SEGURIDAD LEGAL
# =====================================================
client_gemini = None
if os.getenv("GEMINI_API_KEY"):
    client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

system_instruction = (
    "Eres SMARTCARGO CONSULTING. Experto en IATA DGR, PER y LAR. "
    "IMPORTANTE: Siempre incluye: 'Verifique con el manual oficial y la aerolínea'. "
    "Tu objetivo es prevenir el rechazo de carga en almacén."
)

# =====================================================
# 5. ENDPOINTS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Temporalmente abierto para debug
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/cargas")
async def validate_cargo_endpoint(cargo: CargoInput):
    alerts = []
    risk_score = 0
    if cargo.ispm15_seal == "NO":
        alerts.append("R001: Falta sello ISPM-15")
        risk_score += 25
    if cargo.height_cm > 180:
        alerts.append("R002: Altura excede límite ULD")
        risk_score += 20
    if cargo.packing_integrity == "CRITICAL":
        alerts.append("R003: Embalaje dañado")
        risk_score += 50
    
    risk_score = min(risk_score, 100)
    return {"awb": cargo.awb, "alerts": alerts, "alertaScore": risk_score}

@app.post("/advisory")
async def advisory(request: AdvisoryRequest):
    if not client_gemini: raise HTTPException(status_code=503)
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
    if user == ADMIN_USER and password == ADMIN_PASS:
        save_audit(awb=awb or "ADMIN", score=0, alerts=[], status="ADMIN_BYPASS")
        return {"url": f"{FRONTEND_URL}/success.html?access=granted&awb={awb}"}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": description}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"{FRONTEND_URL}/success.html?session_id={{CHECKOUT_SESSION_ID}}&awb={awb}",
        cancel_url=f"{FRONTEND_URL}/cancel.html",
    )
    return {"url": session.url}

@app.get("/")
def health(): return {"status": "Operational", "db_engine": "Ready"}
