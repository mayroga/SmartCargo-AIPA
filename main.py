import os, stripe, httpx, openai, urllib.parse, logging, smtplib
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(title="SmartCargo Advisory by May Roga LLC")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================= ENV =================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))

stripe.api_key = STRIPE_KEY

# ================= STATIC =================
@app.get("/")
async def home():
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
    role: Optional[str] = Form("auto"),
    send_email: Optional[str] = Form(None),
    send_whatsapp: Optional[str] = Form(None)
):
    """
    SMARTCARGO ADVISORY by May Roga LLC - Brain Core
    Genera borradores completos, cálculos y alternativas estratégicas.
    """

    # ================= Brain Core =================
    core_brain = f"""
SMARTCARGO ADVISORY by May Roga LLC
Language: {lang}

IDENTIDAD ASESOR:
- Privado e independiente.
- No certificamos. Generamos borradores y estrategias.

DOCUMENTOS CLAVE:
Aéreo: AWB, HAWB, MAWB, DG Declaration, Dry Ice, Manifest, TSA Known Shipper, Invoice, Packing List
Marítimo: Bill of Lading, House B/L, Manifest, Invoice, Packing, ISF, Shipper Letter
Terrestre: BOL, Delivery Order, Invoice, Packing, Hazmat

REGULACIONES:
- TSA, IATA, CBP, DOT
- Prevención de errores, retrasos o multas
- Estrategias para cargas sobredimensionadas y peligrosas

PESO COBRABLE:
- Si se proporcionan dimensiones (cm):
  Peso Volumétrico = (L*W*H)/6000
  Mayor entre peso bruto y volumétrico = Peso cobrable

MISIÓN:
- Detectar documentos, mercancías y riesgos
- Generar borradores completos
- Formular preguntas estratégicas si faltan datos
- Ofrecer alternativas y soluciones operativas

REGLAS DE RESPUESTA:
1️⃣ CONTROL – Línea de calma y dirección técnica
2️⃣ ACTION – Pasos operativos + Cálculos + Preguntas estratégicas
3️⃣ READY TEXT – Borrador listo para enviar
4️⃣ WHY – Impacto operativo y mitigación de riesgos
5️⃣ CLOSE – Reaseguro de flujo

ESCENARIO CLIENTE:
{prompt}
"""

    guardian_rules = """
FINAL CHECK:
- ¿Calculé peso cobrable si hay dimensiones?
- ¿Generé borrador de todos los documentos?
- ¿Formulé preguntas estratégicas necesarias?
"""

    disclaimer = "\n\nLEGAL NOTE: This advisory is guidance only. Compliance and signatures remain responsibility of Shipper/User."

    system_prompt = core_brain + guardian_rules + disclaimer

    # ================= GEMINI =================
    response_text = ""
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": system_prompt}]}]})
                response_text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    # ================= OPENAI FALLBACK =================
    if not response_text and OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            client_oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.15,
                messages=[{"role": "system", "content": system_prompt}],
                timeout=60.0
            )
            response_text = res.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")

    # ================= ENVIAR EMAIL =================
    if send_email and EMAIL_USER and EMAIL_PASS:
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = send_email
            msg['Subject'] = f"SMARTCARGO Advisory Response"
            msg.attach(MIMEText(response_text, 'plain'))
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, send_email, msg.as_string())
            server.quit()
        except Exception as e:
            logger.error(f"Email sending error: {e}")

    # ================= ENVIAR WHATSAPP =================
    if send_whatsapp:
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(response_text)}"
        response_text += f"\n\nSend via WhatsApp: {whatsapp_url}"

    return {"data": response_text or "SMARTCARGO Advisory analyzing complex request. Retry in a few seconds."}

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
