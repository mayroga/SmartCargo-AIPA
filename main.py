import os, stripe, httpx, openai, urllib.parse, logging
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

# Configuración de Logs para producción
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="SmartCargo Advisory by May Roga LLC")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================= ENV =================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# ================= STATIC (SOLUCIÓN ERROR 405) =================
@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.get("/terms")
async def terms():
    return FileResponse("terms_and_conditions.html")

# ================= CORE ADVISORY =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    role: Optional[str] = Form("auto")
):
    core_brain = f"""
SMARTCARGO ADVISORY by May Roga LLC - CEREBRO OPERATIVO UNIFICADO
Official language: {lang}

PRINCIPIO MADRE: "Si no está claro, no entra. Si no está ordenado, no pasa. Si no está duplicado, no se procesa."

IDENTIDAD ASESOR: Experto en IATA, TSA, DOT, Aduanas.
REGLA DE COPIAS: 
- Aéreo Directo: MAWB (2 ori + 4 copias). 
- Aéreo Consolidado: MAWB (2 ori + 4 copias) + HAWBs sueltos (PROHIBIDO dentro del sobre).
- Marítimo/Terrestre: Suma HAWBs/HBLs = Master.

CAUSAS DE RECHAZO: Ilegibilidad, Shipper No Registrado, DG mal declarada, Pallets sin ISPM-15.
LÓGICA CHOFER: Debe saber si es DG, Courier o Parcial.

REGLAS DE RESPUESTA:
CONTROL – Diagnóstico técnico.
ACTION – Cálculos (LxWxH/6000), Copias y Pasos Operativos.
READY TEXT / DRAFT – Borrador exacto del documento.
WHY – Multas TSA/CBP/DOT y Riesgos.
CLOSE – Reaseguro de flujo.

CONTEXTO: {prompt}
"""
    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides operational drafts. Final compliance is the responsibility of the Shipper/User."
    
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": core_brain + disclaimer}]}]})
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    return {"data": "SMARTCARGO BRAIN is analyzing. Please wait."}

# ================= PAYMENTS =================
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Session - {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/"
        )
        return {"url": checkout.url}
    except Exception:
        return JSONResponse({"error": "Payment Error"}, status_code=400)
