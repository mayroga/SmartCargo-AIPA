import os, stripe, httpx, openai, urllib.parse, logging
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

# Configuración de Logs profesional
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
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")
stripe.api_key = STRIPE_KEY

# ================= STATIC ROUTES =================
@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.get("/terms")
async def terms():
    return FileResponse("terms_and_conditions.html")

# ================= CORE ADVISORY (DOBLE MOTOR) =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("es"),
    role: Optional[str] = Form("auto")
):
    # ORDEN DE MANDO: PROFESOR RESOLUTIVO (ESTUDIO Y PREVENCIÓN)
    system_instruction = f"""
ACTÚA COMO EL PROFESOR TITULAR DE OPERACIONES DE SMARTCARGO ADVISORY BY MAY ROGA LLC.
Tu enfoque es: "Educación basada en la Solución Técnica". Enseñas resolviendo.

REGLAS DE MANDO:
1. RESPUESTA RESOLUTIVA: No preguntes, ENSEÑA LA SOLUCIÓN. Si el usuario plantea un escenario (ej. Pintura), da el dictamen técnico final de inmediato (ej. UN1263).
2. EL EJERCICIO RESUELTO (DRAFT): Entrega siempre el borrador exacto. Es el ejemplo que el usuario debe imitar para cumplir con IATA, TSA, DOT o CBP.
3. CÁLCULO MAGISTRAL: Da la fórmula y el ejemplo resuelto. Calcula Peso Cobrable (/6000 Aire, /1000 Mar/Tierra).
4. LENGUAJE DE ASESOR: Usa "Se recomienda técnicamente", "Borrador de práctica sugerido", "Para fines de estudio y prevención se dicta".
5. NO SOMOS GOBIERNO: Somos una herramienta de estudio y prevención de errores.

ESTRUCTURA OBLIGATORIA:
[CLASE MAGISTRAL] SmartCargo Advisory | Educación Resolutiva.
[DIAGNÓSTICO TÉCNICO] Identificación del riesgo u omisión según normativas.
[CALCULADORA SMARTCARGO] Ejercicio matemático con solución de peso/volumen.
[SOLUCIÓN TÉCNICA (EL DRAFT)] Pasos de ejecución + TEXTO EXACTO para documentos.
[POR QUÉ SE HACE ASÍ] Explicación del riesgo de seguridad y multas (IATA/DOT).
[ESTÁNDAR DE EXAMEN] Qué buscará el oficial de aduana para aprobar su carga.
[CONCLUSIÓN DEL PROFESOR] Movimiento táctico final.

Idioma: {lang}. Rol: {role}. ENTRADA: {prompt}
"""

    # --- MOTOR 1: GEMINI ---
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=45.0) as client:
                payload = {
                    "contents": [{"parts": [{"text": system_instruction}]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048}
                }
                r = await client.post(url, json=payload)
                if r.status_code == 200:
                    res_data = r.json()
                    if "candidates" in res_data:
                        return {"data": res_data["candidates"][0]["content"]["parts"][0]["text"]}
            logger.warning("Gemini no disponible, activando Fallback OpenAI...")
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    # --- MOTOR 2: OPENAI (REDUNDANCIA) ---
    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            client_oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.1,
                messages=[{"role": "system", "content": system_instruction}],
                timeout=45.0
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")

    return {"data": "El aula de SmartCargo está en mantenimiento técnico. Por favor, reintente en unos segundos."}

# ================= APOYO Y PAGOS =================
@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    # Aquí puedes integrar SendGrid o Mailgun. Por ahora logueamos.
    logger.info(f"EMAIL_LOG: Reporte educativo enviado a {email}")
    return {"status": "success"}

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
                    "product_data": {"name": f"Session SmartCargo - {awb}"},
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
        return JSONResponse({"error": "Gateway Error"}, status_code=400)
