import os
import stripe
import httpx
import base64
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Permitir que el navegador acepte respuestas de este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configuración de llaves
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASS_SERVER = os.getenv("ADMIN_PASSWORD", "Ley") # "Ley" es el valor por defecto

stripe.api_key = STRIPE_KEY

class CargoAudit(BaseModel):
    awb: str
    length: float
    width: float
    height: float
    weight: float
    ispm15_seal: str
    unit_system: str

@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    
    # Conversión a CM para lógica de auditoría
    L, W, H = cargo.length, cargo.width, cargo.height
    is_in = cargo.unit_system == "in"

    L_cm = L * 2.54 if is_in else L
    W_cm = W * 2.54 if is_in else W
    H_cm = H * 2.54 if is_in else H

    # Cálculos técnicos
    factor_vol = 166 if is_in else 6000
    vol_m3 = (L_cm * W_cm * H_cm) / 1_000_000
    peso_v = (L * W * H) / factor_vol

    # Reglas de negocio
    if H_cm > 158:
        alerts.append("ALTURA CRÍTICA: No apto para ULD estándar.")
        score += 35
    if cargo.ispm15_seal.upper() == "NO":
        alerts.append("RIESGO MADERA: Sin sello ISPM-15 detectado.")
        score += 40

    return {
        "score": min(score, 100),
        "alerts": alerts,
        "details": f"{vol_m3:.3f} m³ | Peso Vol: {peso_v:.2f}"
    }

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    parts = [{"text": f"Eres SMARTCARGO CONSULTING. Da una respuesta logística breve a: {prompt}"}]

    if image:
        img_data = await image.read()
        parts.append({
            "inline_data": {
                "mime_type": image.content_type,
                "data": base64.b64encode(img_data).decode("utf-8")
            }
        })

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=30.0)
        try:
            answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"data": answer}
        except:
            return {"data": "Error al procesar la respuesta de la IA."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), password: Optional[str] = Form(None)):
    # El éxito redirige al index con el parámetro access=granted
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    
    if password and password.strip() == ADMIN_PASS_SERVER:
        return {"url": success_url}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url="https://smartcargo-aipa.onrender.com/index.html"
    )
    return {"url": session.url}
