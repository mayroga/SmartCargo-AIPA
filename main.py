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

# CONFIGURACIÓN DE VARIABLES DE ENTORNO
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASS_SERVER = os.getenv("ADMIN_PASSWORD") 

stripe.api_key = STRIPE_KEY

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str

@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    L, W, H, WG = cargo.length, cargo.width, cargo.height, cargo.weight
    
    is_in = cargo.unit_system == "in"
    L_cm = L * 2.54 if is_in else L
    H_cm = H * 2.54 if is_in else H
    W_cm = W * 2.54 if is_in else W
    factor_vol = 166 if is_in else 6000

    vol_m3 = (L_cm * W_cm * H_cm) / 1_000_000
    peso_v = (L * W * H) / factor_vol

    if H_cm > 158:
        alerts.append("ALTURA CRÍTICA: No apto para ULD estándar. Solución: Bajar a <158cm.")
        score += 35
    if cargo.ispm15_seal == "NO":
        alerts.append("RIESGO MADERA: Sin sello ISPM-15. Solución: Use paletas de PLÁSTICO o CARTÓN.")
        score += 40
    
    details = f"{vol_m3:.3f} m³ | Vol-W: {peso_v:.2f}"
    return {"score": min(score, 100), "alerts": alerts, "details": details}

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    parts = [{"text": f"Eres SMARTCARGO CONSULTING. Da soluciones técnicas breves. Prompt: {prompt}"}]
    
    if image and image.content_type.startswith("image/"):
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
        except:
            answer = "Error: El asesor no pudo procesar la consulta. Intente solo con texto."
        return {"data": answer}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), password: Optional[str] = Form(None)):
    if password and password == ADMIN_PASS_SERVER:
        return {"url": f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Audit AWB: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}",
        cancel_url="https://smartcargo-aipa.onrender.com/index.html"
    )
    return {"url": session.url}
