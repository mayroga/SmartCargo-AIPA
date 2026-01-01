import os, stripe, httpx, base64
from fastapi import FastAPI, Form, File, UploadFile, List
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- CONFIGURACIÓN DE SEGURIDAD Y PAGOS ---
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "SmartAdmin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "Ley")

# --- MOTOR DE REGLAS TÉCNICAS (TSA / IATA / FLORIDA PORTS) ---
RULES = {
    "R001": {"msg": "Falta Sello ISPM-15 (Madera).", "sol": "Sustituya por pallet de plástico o madera certificada HT para evitar rechazo en aduana.", "lvl": "high"},
    "R002": {"msg": "Altura > 158cm (PAX).", "sol": "Reduzca altura a 63 pulgadas para aviones de pasajeros o reserve en carguero (Freighter).", "lvl": "high"},
    "R003": {"msg": "Exceso de Peso en Base.", "sol": "Distribuya cajas pesadas abajo y ligeras arriba para evitar colapso de corrugado.", "lvl": "medium"},
    "R008": {"msg": "Altura > 213cm (TSA Screening).", "sol": "La carga excede el límite de rayos X de 7 pies. Debe ser deconstruida para inspección física.", "lvl": "high"},
    "R005": {"msg": "DG/Hazmat sin Placarding.", "sol": "Coloque etiquetas Clase 9/UN visibles en los 4 lados según 49 CFR.", "lvl": "high"}
}

@app.post("/cargas")
async def check_cargo(h: float = Form(...), ispm: str = Form(...), dg: str = Form(...), labels: str = Form(...)):
    results = []
    if h > 213: results.append(RULES["R008"])
    elif h > 158: results.append(RULES["R002"])
    if ispm == "NO": results.append(RULES["R001"])
    if dg == "SI": results.append(RULES["R005"])
    if labels == "NO": results.append({"msg": "Etiquetas no visibles.", "sol": "Gire los bultos para que todas las etiquetas miren hacia afuera.", "lvl": "medium"})
    return results

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), images: List[UploadFile] = File(...), extended: bool = Form(False)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    # INSTRUCCIÓN MAESTRA: TSA, IATA, SEGURIDAD EN FLORIDA
    instruction = (
        "Eres SMARTCARGO CONSULTING, el Asesor Virtual experto en logística de Florida (MIA/TPA). "
        "Tu misión es dar SOLUCIONES LEGALES según TSA, IATA y DOT. NUNCA menciones que eres una IA. "
        "Analiza: 1. Tipo de pallet (Madera vs Plástico). 2. Apilamiento y resistencia de cajas. 3. Etiquetas de seguridad. "
        "Si la carga tiene riesgos, indica el paso exacto para rectificar y que sea aceptada hoy mismo. "
        f"{'Análisis Técnico Profundo solicitado.' if extended else 'Análisis Ejecutivo.'}"
    )

    parts = [{"text": f"{instruction}\n\nConsulta: {prompt}"}]
    for img in images[:3]: # Límite de 3 fotos
        img_data = await img.read()
        parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(img_data).decode("utf-8")}})

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=50.0)
        try:
            return {"data": res.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except:
            return {"data": "El Asesor está verificando los manuales de cumplimiento. Reintente."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Asesoría Técnica AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}
