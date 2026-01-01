import os, stripe, httpx, base64
from fastapi import FastAPI, Form, File, UploadFile, List
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# --- BASE DE DATOS TÉCNICA DE RIESGOS (Basado en standards.js) ---
ALERTS_DB = {
    "R001": {"msg": "Pallet sin sello ISPM-15.", "desc": "Riesgo fitosanitario. Carga puede ser devuelta.", "level": "high"},
    "R002": {"msg": "Altura > 158cm (PAX).", "desc": "No apto para avión de pasajeros. Solo Freighter.", "level": "high"},
    "R004": {"msg": "Etiquetas no visibles.", "desc": "Incumplimiento de visibilidad TSA/IATA.", "level": "medium"},
    "R005": {"msg": "Mercancía Peligrosa (DG).", "desc": "Requiere NOTOC y etiquetas Clase 9/UN visibles.", "level": "high"},
    "R008": {"msg": "Altura > 213cm.", "desc": "Excede límite de screening TSA. Requiere re-paletizado.", "level": "high"},
    "R009": {"msg": "Discrepancia de seguridad.", "desc": "Revisar integridad del embalaje y sellos.", "level": "medium"}
}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Configuración de Entorno
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_USER_SERVER = os.getenv("ADMIN_USERNAME", "SmartAdmin")
ADMIN_PASS_SERVER = os.getenv("ADMIN_PASSWORD", "Ley")

@app.post("/cargas")
async def process_audit(h: float = Form(...), ispm: str = Form(...), dg: str = Form(...), labels: str = Form(...)):
    results = []
    # Aplicación de reglas técnicas
    if h > 213: results.append(ALERTS_DB["R008"])
    elif h > 158: results.append(ALERTS_DB["R002"])
    
    if ispm == "NO": results.append(ALERTS_DB["R001"])
    if dg == "SI": results.append(ALERTS_DB["R005"])
    if labels == "NO": results.append(ALERTS_DB["R004"])
    
    return results

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), images: List[UploadFile] = File(...)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    instruction = (
        "Eres SMARTCARGO CONSULTING. Analiza estas imágenes (máximo 3 ángulos). "
        "Busca: 1. Sello ISPM-15. 2. Etiquetas de orientación. 3. Daños en el embalaje. "
        "Provee una respuesta técnica, estable y que inspire confianza al operario."
    )

    parts = [{"text": f"{instruction}\n\nConsulta: {prompt}"}]
    
    # Procesamos hasta 3 fotos para el análisis visual
    for img in images[:3]:
        img_data = await img.read()
        parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(img_data).decode("utf-8")}})

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=40.0)
        try:
            return {"data": res.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except:
            return {"data": "Error en el análisis visual. Intente con imágenes de menor tamaño."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    
    # Lógica de Blindaje Administrativo
    if user == ADMIN_USER_SERVER and password == ADMIN_PASS_SERVER:
        return {"url": success_url}
    
    # Lógica de Pago Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Asesoría AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}
