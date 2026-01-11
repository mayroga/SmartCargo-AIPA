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
    allow_origins=["*"],  # Cambiar por dominio real en producción
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

# ================= STATIC =================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.get("/terms")
async def terms():
    return FileResponse("terms.html")

# ================= CORE ADVISORY =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    role: Optional[str] = Form("auto")
):
    """
    SMARTCARGO ADVISORY by May Roga LLC - Brain Core
    Genera soluciones estratégicas para problemas de carga aérea, marítima y terrestre
    incluyendo DG, Dry Ice, Hazmat, TSA, IATA, CBP y más.
    """
    core_brain = f"""
SMARTCARGO ADVISORY by May Roga LLC
Official language: {lang}

IDENTIDAD DEL ASESOR:
- Asesoría logística privada e independiente.
- No somos autoridad (DOT, TSA, CBP, IATA) y no certificamos documentos.
- Generamos borradores, guías operativas y soluciones estratégicas.

DOCUMENTOS QUE DOMINAMOS:
AÉREO: AWB, HAWB, MAWB, DG Declaration, Dry Ice Statement, Manifest, TSA Known Shipper, Invoice, Packing List
MARÍTIMO: Bill of Lading, House B/L, Manifest, Invoice, Packing List, ISF, Shipper Letter
TERRESTRE: BOL, Delivery Order, Invoice, Packing List, Hazmat

CAPACIDADES:
- Detectar inconsistencias, riesgos y problemas en documentos.
- Calcular peso cobrable automático si hay dimensiones.
- Ofrecer alternativas de solución claras y prácticas.
- Explicar el impacto operativo de cada riesgo detectado.
- Preparar borradores listos para revisión del cliente.
- Cobertura completa de DG, Dry Ice, TSA, IATA, CBP y regulaciones marítimas y terrestres.

REGLAS DE RESPUESTA:
1️⃣ CONTROL – Línea de calma y dirección técnica.
2️⃣ ACTION – Pasos operativos, cálculos, preguntas estratégicas y alternativas de solución.
3️⃣ READY TEXT / DRAFT – Mensaje listo o borrador.
4️⃣ WHY – Impacto operativo y prevención de retrasos, multas o retornos.
5️⃣ CLOSE – Reaseguro del flujo logístico.

PREGUNTAS ESTRATÉGICAS CLAVE:
- ¿Shipper y Consignee completos?
- ¿Airport Codes correctos?
- ¿Peso bruto y dimensiones disponibles? Calcular peso volumétrico.
- ¿Uso de Dry Ice o mercancía peligrosa? Clase, cantidad, UN Number.
- ¿Incoterm, moneda, descripción de Invoice?
- ¿Packing List: Net/Gross, dimensiones, tipo de packing, marks & numbers?
- ¿House B/L y manifiestos completos con copias adecuadas?
- ¿Courier y documentos legibles?

CONTEXTO DEL USUARIO:
{prompt}
"""

    guardian_rules = """
FINAL CHECK:
- ¿Calculé peso cobrable correctamente?
- ¿Generé borrador de todos los documentos solicitados?
- ¿Proporcioné alternativas de solución claras y viables para cada problema detectado?
"""

    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides operational drafts and strategic guidance. Final compliance is responsibility of shipper/user."

    system_prompt = core_brain + guardian_rules + disclaimer

    # ================= GEMINI =================
    if GEMINI_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            )
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    url,
                    json={"contents": [{"parts": [{"text": system_prompt}]}]}
                )
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    return {"data": text}
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    # ================= OPENAI FALLBACK =================
    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            client_oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.15,
                messages=[{"role": "system", "content": system_prompt}],
                timeout=60.0
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")

    return {"data": "SMARTCARGO ADVISORY is analyzing a complex request. Please retry in a few seconds."}

# ================= PAYMENTS =================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # Bypass administrativo
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}

    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"SmartCargo Advisory Session – {awb}"},
                    "unit_amount": int(amount * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/"
        )
        return {"url": checkout.url}
    except Exception as e:
        logger.error(f"Stripe Error: {e}")
        return JSONResponse({"error": "Payment gateway error"}, status_code=400)
