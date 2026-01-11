import os, stripe, httpx, openai, urllib.parse, logging
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="SmartCargo Advisory by May Roga LLC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================= ENV =================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = STRIPE_KEY

# ================= ROUTES =================
@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

# ================= CORE ADVISORY (CEREBRO DOBLE MOTOR) =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("es"),
    role: Optional[str] = Form("auto")
):
    # ORDEN DE MANDO MAESTRA PARA AMBAS IAs
    system_instruction = f"""
ACTÚA COMO EL CEREBRO OPERATIVO DE SMARTCARGO ADVISORY BY MAY ROGA LLC.
1. IDENTIDAD: Asesor Senior Multimodal. No eres gobierno. 
2. LENGUAJE TÉCNICO: Usa "Se recomienda técnicamente", "Borrador sugerido (Draft)".
3. CÁLCULO OBLIGATORIO: Si hay medidas, calcula Volumen y Peso Cobrable (/6000 Aire, /1000 Mar). Altura > 160cm = "CAO - Cargo Aircraft Only".
4. DG & RIESGOS: Identifica UN Numbers y Clases. Detén la operación si hay "Undeclared DG".
5. SOLUCIÓN TOTAL: No derives al cliente. TÚ ERES LA SOLUCIÓN FINAL.

ESTRUCTURA: [AVISO LEGAL], [CONTROL], [CALCULADORA], [ACTION + DRAFT], [ESTÁNDAR COUNTER], [WHY], [CLOSE].
Idioma: {lang}. Rol: {role}. ENTRADA: {prompt}
"""

    # --- INTENTO 1: GEMINI ---
    if GEMINI_KEY:
        try:
            # URL actualizada para evitar el 404
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "contents": [{"parts": [{"text": system_instruction}]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048}
                }
                r = await client.post(url, json=payload)
                if r.status_code == 200:
                    res_data = r.json()
                    if "candidates" in res_data:
                        return {"data": res_data["candidates"][0]["content"]["parts"][0]["text"]}
            logger.warning("Gemini falló, intentando Fallback con OpenAI...")
        except Exception as e:
            logger.error(f"Error Gemini: {e}")

    # --- INTENTO 2: OPENAI (FALLBACK) ---
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
            logger.error(f"Error OpenAI Fallback: {e}")

    return {"data": "SISTEMA SMARTCARGO EN SOBRECARGA. Ni Gemini ni OpenAI respondieron. Reintente en 10 segundos."}

# ================= OTROS ENDPOINTS =================
@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    return {"status": "success"}

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
    except: return JSONResponse({"error": "Error de Pago"}, status_code=400)
