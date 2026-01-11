import os, stripe, httpx, openai, urllib.parse, logging
from fastapi import FastAPI, Form
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
    role: Optional[str] = Form("auto")
):
    # ================= Brain Core Resolutivo =================
    core_brain = f"""
IDENTIDAD: SMARTCARGO ADVISORY by May Roga LLC.
AVISO LEGAL: ASESORÍA PRIVADA INDEPENDIENTE. NO SOMOS IATA, DOT, TSA O CBP.
Tu misión es dar SOLUCIONES Y SUGERENCIAS ESTRATÉGICAS para evitar rechazos en counter.

REGLAS DE MANDO:
1. CALCULADORA: Si ves medidas (cm/in), CALCULA el Peso Volumétrico (L*W*H/6000 para aire, /1000 para mar) y da el PESO COBRABLE.
2. RESOLUCIÓN: Si hay problemas (madera, roturas, DG), da la solución técnica física inmediata.
3. DRAFTS: Proyecta borradores de textos para AWB, B/L o BOL. No digas "deberías", di "Aquí tienes el borrador".
4. LENGUAJE: Técnico, seco, ejecutivo, proactivo. Evita palabras como "illegal" o "penalty", usa "operational risk".

ESTRUCTURA DE RESPUESTA:
[AVISO LEGAL] SmartCargo Advisory by May Roga LLC | Asesoría Privada Independiente.
[CONTROL] Diagnóstico experto del riesgo.
[CALCULADORA SMARTCARGO] Resultados matemáticos de volumen y peso.
[ACTION - SOLUCIÓN] Protocolo de Solución y Borrador Documental.
[WHY] El costo de no seguir esta asesoría (Multas, Dead Freight, Retornos).
[CLOSE] Siguiente paso operativo.

CONTEXTO DE SESIÓN ({lang}):
{prompt}
"""

    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides operational drafts and strategic guidance. This is not a legal certification. Final compliance and signatures are the responsibility of the Shipper/User."
    system_prompt = core_brain + disclaimer

    # ================= GEMINI =================
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": system_prompt}]}]})
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return {"data": text}
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    # Fallback OpenAI
    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            client_oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.1,
                messages=[{"role": "system", "content": system_prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception: pass

    return {"data": "SMARTCARGO BRAIN is busy. Please retry."}

@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    # Aquí puedes integrar SendGrid o Mailgun en el futuro. Por ahora simula éxito.
    logger.info(f"Reporte enviado a: {email}")
    return {"status": "success"}

# ================= PAYMENTS =================
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}

    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Advisory Session – {awb}"},
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
