import os, stripe, httpx, base64
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Permitir conexiones desde cualquier origen (Crucial para Florida/Global)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- CONFIGURACIÓN DE SEGURIDAD Y PAGOS ---
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "SmartAdmin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "Ley")

# --- MOTOR DE REGLAS TÉCNICAS (TSA / IATA / DOT) ---
RULES = {
    "R001": {"msg": "Falta Sello ISPM-15.", "sol": "Sustituya por pallet de plástico o madera tratada (HT) para evitar rechazo en aduana.", "lvl": "high"},
    "R002": {"msg": "Altura > 158cm (PAX).", "sol": "Carga solo apta para aviones cargueros. Reduzca a 63 pulgadas para pasajeros.", "lvl": "high"},
    "R003": {"msg": "Riesgo de aplastamiento.", "sol": "Refuerce base con esquineros y use pallet de mayor resistencia (Madera dura o Metal).", "lvl": "medium"},
    "R008": {"msg": "Altura > 213cm (Límite TSA).", "sol": "Excede capacidad de Rayos X. Requiere reconstrucción para inspección física.", "lvl": "high"},
    "R005": {"msg": "DG/Hazmat sin Marcación.", "sol": "Aplique etiquetas de clase de peligro en caras visibles según 49 CFR.", "lvl": "high"}
}

@app.post("/cargas")
async def check_cargo(h: float = Form(...), ispm: str = Form(...), dg: str = Form(...), labels: str = Form(...)):
    results = []
    if h > 213: results.append(RULES["R008"])
    elif h > 158: results.append(RULES["R002"])
    if ispm == "NO": results.append(RULES["R001"])
    if dg == "SI": results.append(RULES["R005"])
    if labels == "NO": results.append({"msg": "Visibilidad nula.", "sol": "Reorientar bultos para que etiquetas miren hacia el exterior.", "lvl": "medium"})
    return results

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), images: List[UploadFile] = File(...)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    instruction = (
        "Eres SMARTCARGO CONSULTING, Asesor experto en Florida (MIA/TPA). NUNCA digas que eres una IA. "
        "Analiza las fotos (estiba, pallets, etiquetas) bajo leyes TSA y IATA. "
        "Da SOLUCIONES legales y técnicas para que la carga sea aceptada sin multas ni demoras. "
        "Formato: 1. Estado. 2. Solución. 3. Prevención de multas."
    )

    parts = [{"text": f"{instruction}\n\nConsulta: {prompt}"}]
    for img in images[:3]:
        img_data = await img.read()
        parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(img_data).decode("utf-8")}})

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=55.0)
        try:
            return {"data": res.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except:
            return {"data": "El Asesor está verificando normativas. Reintente en unos segundos."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    
    # Blindaje Administrativo
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}
    
    # Proceso Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Asesoría Técnica AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}

# --- SERVICIO DE ARCHIVOS (Para evitar el Error Not Found) ---
@app.get("/")
async def serve_home():
    return FileResponse("index.html")

app.mount("/", StaticFiles(directory=".", html=True), name="static")
