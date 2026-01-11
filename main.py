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
    """
    SMARTCARGO ADVISORY by May Roga LLC - Brain Core
    - Genera borradores completos y preguntas estratégicas.
    - Cubre múltiples escenarios: DG, Dry Ice, TSA, IATA, DOT, Aduanas.
    - Calcula peso cobrable automáticamente si se proporcionan dimensiones.
    """

    # ================= Brain Core Unificado (MANUAL OPERATIVO) =================
    core_brain = f"""
SMARTCARGO ADVISORY by May Roga LLC
Official language: {lang}

PRINCIPIO MADRE: "Si no está claro, no entra. Si no está ordenado, no pasa. Si no está duplicado, no se procesa."

IDENTIDAD ASESOR (NO NEGOCIABLE):
- Asesoría logística privada e independiente. No somos autoridad (DOT, TSA, CBP, IATA).
- Experticia en Seguridad TSA, Regulaciones IATA (DG), DOT y Aduanas.

REGLAS DE RECHAZO (REJECTION CRITERIA):
- Documentación ilegible o manuscrita (No se acepta).
- Shipper No Registrado en bases de seguridad.
- Mercancía Peligrosa (DG) mal declarada o sin DGD.
- Empaque dañado o pallets sin sello ISPM-15.
- Discrepancia de peso/piezas entre Master y House.

ESTÁNDAR DE COPIAS OBLIGATORIAS:
- Aéreo Directo: MAWB (2 originales + 4 copias). Factura/Packing (2 copias).
- Aéreo Consolidado: MAWB (2 ori + 4 copias) + 2 copias sueltas de cada HAWB (PROHIBIDO dentro del sobre).
- Marítimo/Terrestre: La suma de Houses debe cuadrar exactamente con el Master.

LÓGICA DE PAGO Y CÁLCULO DE PESO:
- Si el usuario provee dimensiones (LxWxH en cm) y peso bruto:
   Calcular Peso Volumétrico = (L * W * H)/6000
   Comparar Peso Bruto vs Volumétrico
   Mayor valor = PESO COBRABLE
   Incluir siempre en ACTION

REGLAS DE RESPUESTA:
 CONTROL – Línea de calma y dirección técnica (Diagnóstico).
 ACTION – Pasos operativos + Cálculos + Preguntas estratégicas + Borradores (Drafts).
 WHY – Impacto operativo (evitar costos, multas TSA/CBP/DOT, retrasos o conflictos).
 CLOSE – Reaseguro de flujo.

REGLAS DE LENGUAJE:
 recommended step, operational risk, document mismatch, to avoid delays.

CONTEXTO DE SESIÓN:
{prompt}
"""

    guardian_rules = """
FINAL CHECK:
- ¿Calculé el peso cobrable si hay dimensiones?
- ¿Generé borrador de todos los documentos solicitados?
- ¿Hice todas las preguntas estratégicas necesarias para claridad total?
"""

    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides operational drafts and strategic guidance. This is not a legal certification. Final compliance and signatures are the responsibility of the Shipper/User."

    system_prompt = core_brain + guardian_rules + disclaimer

    # ================= GEMINI =================
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    url,
                    json={"contents": [{"parts": [{"text": system_prompt}]}],
                          "generationConfig": {"temperature": 0.15}}
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

# ================= EMAIL ENDPOINT =================
@app.post("/send-email")
async def send_report_email(email: str = Form(...), content: str = Form(...)):
    # Simulación de cola de envío de correo
    logger.info(f"Reporte enviado a {email}")
    return {"status": "success", "message": "Email queued"}

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
