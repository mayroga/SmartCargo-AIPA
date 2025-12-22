import os
import stripe
import httpx
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
app = FastAPI()

# --- CONFIGURACIÓN ---
FRONTEND_URL = "https://smartcargo-advisory.onrender.com"
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "secret123")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- DB SETUP ---
def get_db_url():
    url = os.getenv("DATABASE_URL", "sqlite:///./backup.db")
    if url.startswith("postgres://"): url = url.replace("postgres://", "postgresql://", 1)
    return url

engine = create_engine(get_db_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditRecord(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    awb = Column(String); risk_score = Column(Integer); alerts = Column(JSON); status = Column(String)

Base.metadata.create_all(bind=engine)

# --- IA BILINGÜE Y LEGAL ---
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
SYSTEM_INSTRUCTION = (
    "Eres SMARTCARGO CONSULTING. Eres un ASESOR LOGÍSTICO BILINGÜE (Español/Inglés). "
    "Tu función es solo asesoría. No clasificas, no inspeccionas, no trasladas carga. "
    "Analiza fotos buscando daños en embalajes o falta de etiquetas IATA. "
    "IMPORTANTE: Siempre finaliza con: 'Reporte preventivo. Consulte manuales oficiales'."
)

# --- MODELS ---
class CargoInput(BaseModel):
    awb: str; content: str; height_cm: float; dg_type: str; ispm15_seal: str; email: Optional[str] = None

# --- ENDPOINTS ---
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/cargas")
async def validate_cargo(cargo: CargoInput):
    alerts = []
    score = 0
    if cargo.ispm15_seal == "NO": alerts.append("Riesgo Fitosanitario: Falta Sello ISPM-15"); score += 30
    if cargo.height_cm > 160: alerts.append("Alerta de Estiba: Altura superior a ULD estándar"); score += 20
    if "lithium" in cargo.content.lower(): alerts.append("DGR: Contiene Baterías de Litio (Revisar PI 965)"); score += 40
    return {"alerts": alerts, "alertaScore": min(score, 100)}

@app.post("/advisory")
async def advisory(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    contents = [prompt]
    if image:
        img_bytes = await image.read()
        contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
    
    response = client_gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
    )
    return {"data": response.text}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: str = Form(None), password: str = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{FRONTEND_URL}/index.html?access=granted&awb={awb}"}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Auditoría AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"{FRONTEND_URL}/index.html?access=granted&awb={awb}",
        cancel_url=f"{FRONTEND_URL}/index.html",
    )
    return {"url": session.url}

@app.get("/")
def health(): return {"status": "AIPA Live", "mode": "Advisory Only"}
