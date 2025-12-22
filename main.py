import os
import stripe
import httpx
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# CONFIGURACIÓN
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASS = "tu_clave_aqui" # CAMBIA ESTO POR TU CLAVE

stripe.api_key = STRIPE_KEY

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str

@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    L, W, H, WG = cargo.length, cargo.width, cargo.height, cargo.weight
    
    if cargo.unit_system == "in":
        L_cm, H_cm = L * 2.54, H * 2.54
        factor_vol = 166
    else:
        L_cm, H_cm = L, H
        factor_vol = 6000

    vol_m3 = (L_cm * (W * (2.54 if cargo.unit_system == "in" else 1)) * H_cm) / 1_000_000
    peso_v = (L * cargo.width * H) / factor_vol

    if H_cm > 158:
        alerts.append("Altura crítica. / Excessive height.")
        score += 35
    if cargo.ispm15_seal == "NO":
        alerts.append("Madera sin sello. / Wood no seal.")
        score += 40
    
    return {"score": min(score, 100), "alerts": alerts, "details": f"{vol_m3:.3f} m3 | Vol-W: {peso_v:.2f}"}

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: UploadFile = File(None)):
    # Usamos HTTPX directo para evitar errores de librería
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Eres SMARTCARGO CONSULTING. Responde en el idioma del usuario de forma breve. {prompt}"}]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        data = response.json()
        try:
            answer = data['candidates'][0]['content']['parts'][0]['text']
        except:
            answer = "Error de conexión con Gemini. Verifica tu API Key."
        return {"data": answer}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    
    # BYPASS DE ADMIN
    if password == ADMIN_PASS:
        return {"url": success_url}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Audit {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url="https://smartcargo-aipa.onrender.com/index.html"
    )
    return {"url": session.url}
