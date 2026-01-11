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
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.get("/terms")
async def terms(): return FileResponse("terms_and_conditions.html")

# ================= CORE ADVISORY =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("es"),
    role: Optional[str] = Form("auto")
):
    # ================= Brain Core Resolutivo =================
    core_brain = f"""
IDENTIDAD: SMARTCARGO ADVISORY by May Roga LLC.
AVISO LEGAL: ASESORÍA PRIVADA INDEPENDIENTE. NO SOMOS IATA, DOT, TSA O CBP.
Tu misión es dar SOLUCIONES Y SUGERENCIAS ESTRATÉGICAS para evitar rechazos en counter.

REGLAS DE MANDO (ESTRICTAS):
1. CALCULADORA: Si detectas medidas (LxWxH), CALCULA el Peso Volumétrico (Aéreo /6000, Marítimo /1000) y define el PESO COBRABLE.
2. RESOLUCIÓN: Si hay problemas (madera, roturas, DG), da la solución técnica física. No digas "consulte", di "Aquí está el protocolo".
3. DRAFTS: Proyecta borradores de textos para AWB, B/L o BOL. Escribe el texto exacto.
4. LENGUAJE: Técnico, ejecutivo, resolutivo. Usa "Protocolo de Solución" y "Diagnóstico de Riesgo".

ESTRUCTURA DE RESPUESTA:
[AVISO LEGAL] SmartCargo Advisory by May Roga LLC | Asesoría Privada Independiente. No somos autoridad gubernamental.
[CONTROL] Diagnóstico experto del riesgo.
[CALCULADORA SMARTCARGO] Resultados matemáticos (Peso Volumétrico vs Bruto).
[ACTION - SOLUCIÓN] Protocolo técnico + Borrador del documento (AWB/BL/BOL).
[ESTÁNDAR DE COUNTER] Lo que el inspector rechazará si no corriges.
[WHY] El costo de no seguir esta asesoría (Multas, Dead Freight, Retornos).
[CLOSE] Siguiente paso operativo.

Contexto de Sesión: {prompt} | Rol: {role} | Idioma: {lang}
"""

    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides operational drafts and strategic guidance. Final compliance and signatures are the responsibility of the Shipper/User."
    system_prompt = core_brain + disclaimer

    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json={
                    "contents": [{"parts": [{"text": system_prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                })
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    return {"data": "Cerebro SmartCargo en calibración. Intente de nuevo."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}

@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    logger.info(f"Enviando reporte a {email}")
    return {"status": "success"}
