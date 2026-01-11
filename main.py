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

# ================= STATIC =================
# Ajustado para permitir HEAD (Render Health Check) y evitar Error 405
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
    """

    # ================= Brain Core (INSTRUCCIONES ENDURECIDAS) =================
    core_brain = f"""
SMARTCARGO ADVISORY by May Roga LLC
Official language: {lang}

IDENTIDAD ASESOR (NO NEGOCIABLE):
- Eres un Experto Resolutivo. Tu lenguaje es técnico y directo.
- No eres gobierno. Eres asesoría privada (IATA, TSA, DOT, Aduana).
- Si hay un riesgo (ej. DG no declarado), DETÉN la operación y da la solución.

MISION DE SOLUCIÓN:
- CÁLCULOS: Si hay medidas, calcula Volumen y Peso Cobrable de inmediato.
- DG/DRY ICE: Identifica UN Number, Clase y texto exacto para el AWB.
- RECHAZOS: Advierte sobre ilegibilidad, falta de copias sueltas o falta de sellos ISPM-15.
- ASISTENCIA TOTAL: No envíes al cliente con otros. Tú das la respuesta técnica.

REGLAS DE RESPUESTA:
 CONTROL – Diagnóstico técnico del riesgo.
 ACTION – Pasos operativos + Cálculos + DRAFT (Texto exacto para copiar).
 READY TEXT / DRAFT – Mensaje listo para enviar o poner en el documento.
 WHY – Impacto de multas federales o retrasos.
 CLOSE – Instrucción final de despacho.

REGLAS DE LENGUAJE:
- Se recomienda técnicamente, Borrador sugerido, Bajo estándar normativo.

CONTEXTO DE SESIÓN:
{prompt}
"""

    guardian_rules = """
FINAL CHECK:
- ¿Calculé el peso cobrable? ¿Di el texto exacto para el borrador? 
- ¿Asistí al cliente con una solución definitiva?
"""

    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides strategic operational drafts. This is not a legal certification. Final compliance is responsibility of the user."

    system_prompt = core_brain + guardian_rules + disclaimer

    # ================= MOTOR DE IA =================
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": system_prompt}]}],
                        "generationConfig": {"temperature": 0.1} # Máxima precisión técnica
                    }
                )
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return {"data": text}
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    return {"data": "SMARTCARGO ADVISORY is processing. Please retry."}

# ================= EMAIL ENDPOINT =================
@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    logger.info(f"Reporte enviado a: {email}")
    return {"status": "success"}

# ================= PAYMENTS (ORIGINAL) =================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
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
