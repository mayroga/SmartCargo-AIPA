import os, stripe, httpx, openai, urllib.parse, logging
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

# Configuración de Logs
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

# ================= ROUTES =================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

# ================= CORE ADVISORY ENGINE =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    role: Optional[str] = Form("auto")
):
    """
    SMARTCARGO ADVISORY - Brain Core Unificado (Aire, Mar, Tierra)
    Asesoría técnica para mitigar riesgos, demoras y costos operativos.
    """

    system_logic = f"""
IDENTIDAD: SmartCargo Advisory by May Roga LLC.
ROL: Asesor técnico privado e independiente. NO somos autoridad gubernamental (TSA, CBP, DOT, IATA).
OBJETIVO: Prevenir errores operativos antes de que la carga llegue al counter o puerto.

PRINCIPIOS MADRE:
1. "Si no está claro, no entra. Si no está ordenado, no pasa."
2. Semáforo de Riesgo: 
   - VERDE: Alineado con estándares. 
   - AMARILLO: Sugerencia de corrección necesaria. 
   - ROJO: Inconsistencia crítica detectada.

INTELIGENCIA MULTIMODAL:
- AÉREO: Validar MAWB/HAWB, TSA Known Shipper, DG IATA, Dry Ice (UN1845).
- MARÍTIMO: Validar MBL/HBL, VGM (Peso Verificado), ISPM-15, IMO (IMDG Code).
- TERRESTRE: BOL, Pesos por eje, Sujeción de carga, Horas de servicio.

LÓGICA DE CÁLCULO (Peso Cobrable):
- Aéreo: (L*W*H)/6000 | Marítimo: (L*W*H)/1000.
- El mayor entre Peso Bruto y Volumétrico es el SUGGESTED CHARGEABLE WEIGHT.

REGLAS DE LENGUAJE SEGURO:
- Prohibido usar: "Illegal", "Violation", "Fine", "Must", "Authority".
- Usar siempre: "Operational risk", "Document mismatch", "Suggested step", "Non-standard".

ESTRUCTURA DE RESPUESTA:
- [CONTROL] Diagnóstico técnico.
- [ACTION] Pasos operativos sugeridos + Cálculos + Borradores (Drafts).
- [WHY] Riesgo de demora o costo extra si no se corrige.
- [CLOSE] Reaseguro del flujo operativo.

Idioma: {lang}
Contexto: {prompt}
"""

    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides operational drafts and strategic guidance. Final compliance, signatures, and legal responsibility are of the Shipper/User."
    full_prompt = system_logic + disclaimer

    # --- GEMINI EXECUTION ---
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": full_prompt}]}]})
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    # --- OPENAI FALLBACK ---
    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            client_oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.2,
                messages=[{"role": "system", "content": full_prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")

    return {"data": "Advisory System temporarily busy. Please retry."}

# ================= PAYMENTS =================
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Session {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/"
        )
        return {"url": checkout.url}
    except Exception as e:
        return JSONResponse({"error": "Gateway Error"}, status_code=400)
