import os
import stripe
import httpx
import base64
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# CONFIGURACIÓN DE ENTORNO
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") # Tu clave configurada en Render

stripe.api_key = STRIPE_KEY

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str

@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    is_in = cargo.unit_system == "in"
    
    # Conversión técnica
    L_cm = cargo.length * 2.54 if is_in else cargo.length
    H_cm = cargo.height * 2.54 if is_in else cargo.height
    W_cm = cargo.width * 2.54 if is_in else cargo.width
    
    vol_m3 = (L_cm * W_cm * H_cm) / 1_000_000
    peso_v = (cargo.length * cargo.width * cargo.height) / (166 if is_in else 6000)

    if H_cm > 158: 
        alerts.append("Altura crítica (>158cm). Solución: Re-estibar cajas.")
        score += 35
    if cargo.ispm15_seal == "NO": 
        alerts.append("Madera sin sello ISPM-15. Solución: Usar paleta de plástico.")
        score += 40
    
    return {
        "score": min(score, 100), 
        "alerts": alerts, 
        "details": f"{vol_m3:.3f} m³ | Peso-Vol: {peso_v:.2f}"
    }

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    # ESTRUCTURA HÍBRIDA: Siempre envía texto, adjunta imagen si existe
    parts = [{"text": f"Eres SMARTCARGO CONSULTING. Experto bilingüe IATA. Responde breve y técnico: {prompt}"}]
    
    if image:
        img_data = await image.read()
        parts.append({
            "inline_data": {
                "mime_type": image.content_type,
                "data": base64.b64encode(img_data).decode("utf-8")
            }
        })
    
    payload = {"contents": [{"parts": parts}]}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            res_json = response.json()
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            return {"data": answer}
        except Exception:
            return {"data": "Error: El asesor no pudo procesar la consulta. Intente con texto breve."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), password: Optional[str] = Form(None)):
    # BYPASS DE ADMINISTRADOR
    if password and password == ADMIN_PASSWORD:
        return {"url": f"https://smartcargo-aipa.onrender.com/index.html?access=granted&admin=true&awb={awb}"}
    
    # PROCESO DE PAGO STRIPE
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Audit {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}",
        cancel_url="https://smartcargo-aipa.onrender.com/index.html"
    )
    return {"url": session.url}
