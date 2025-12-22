import os, stripe, httpx, base64
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASS_SERVER = os.getenv("ADMIN_PASSWORD", "Ley")

@app.post("/cargas")
async def process_audit(role: str = Form(...), h: float = Form(...), ispm: str = Form(...), dg: str = Form(...), labels: str = Form(...)):
    results = []
    
    # Lógica Transversal (Seguridad de Vuelo)
    if h > 158:
        results.append({"msg": "VASCULERO/RAMPA: Altura excede 158cm. No apto para Avión de Pasajeros (PAX). Solo Freighter.", "level": "high"})
    
    if ispm == "NO":
        results.append({"msg": "COUNTER/ADUANA: Sin sello ISPM-15. Riesgo de confiscación y multa fitosanitaria.", "level": "high"})

    if dg == "SI":
        results.append({"msg": "OPERATIVO: Mercancía Peligrosa. Verificar 'NOTOC' para el Capitán y etiquetas UN visibles.", "level": "high"})

    if labels == "NO":
        results.append({"msg": "GENERAL: Todo label (Orientación, TSA, DG) DEBE estar hacia afuera para inspección rápida.", "level": "high"})

    return results

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    instruction = (
        "Eres SMARTCARGO CONSULTING. Tu misión es asesorar a: Shippers, Camioneros, Counters, Vasculeros y Operarios de Rampa. "
        "Reglas: 1. Labels siempre visibles. 2. Altura máxima 158cm para PAX. 3. Madera siempre sellada. 4. DG requiere etiquetas Clase 9/UN. "
        "Si ves la imagen, analiza la integridad del pallet y la posición de las marcas de seguridad."
    )

    parts = [{"text": f"{instruction}\n\nConsulta técnica: {prompt}"}]
    if image:
        img_data = await image.read()
        parts.append({"inline_data": {"mime_type": image.content_type, "data": base64.b64encode(img_data).decode("utf-8")}})

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=30.0)
        try:
            return {"data": res.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except:
            return {"data": "Error en el análisis. Verifique la conexión o el tamaño de la imagen."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    if password and password.strip() == ADMIN_PASS_SERVER:
        return {"url": success_url}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Consultoría AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}
