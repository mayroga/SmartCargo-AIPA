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
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# ================= ROUTES (SOPORTE GET Y HEAD PARA EVITAR 405) =================
@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

# ================= CORE ADVISORY (EL ASESOR TÉCNICO RESOLUTIVO) =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("es"),
    role: Optional[str] = Form("auto")
):
    # INSTRUCCIONES DE MANDO: LENGUAJE DE ASESORÍA EXPERTA Y SEGURA
    system_instruction = f"""
Eres el CEREBRO OPERATIVO de SMARTCARGO ADVISORY by May Roga LLC.
TU ROL: Asesor Técnico Independiente Senior. 
TU MISIÓN: Dar soluciones definitivas. No eres gobierno, no emites licencias, eres el experto que dice CÓMO HACERLO BIEN para evitar multas.

REGLAS DE MANDO (ESTRICTAS):
1. LENGUAJE DE ASESOR: Usa "Se recomienda técnicamente", "El estándar sugiere", "Borrador sugerido (Draft)". Evita términos de autoridad gubernamental.
2. CÁLCULO OBLIGATORIO: Si hay medidas, calcula el volumen y peso volumétrico (Aire /6000, Mar/Tierra /1000). Dictamina el Chargeable Weight.
3. PROTOCOLO DG/HIELO SECO: Identifica UN Number y Clase. Da el texto EXACTO para el documento.
4. ALTURA CRÍTICA: Si excede 160cm (63"), declara "CAO (Cargo Aircraft Only)" para aviones de carga.
5. NO DERIVAR: Tú eres la solución final. No envíes al cliente con otros asesores.

ESTRUCTURA DE RESPUESTA:
[AVISO DE ASESORÍA] SmartCargo Advisory by May Roga LLC | Asesoría Privada Independiente.
[CONTROL - DIAGNÓSTICO] Identificación técnica del escenario.
[CALCULADORA SMARTCARGO] Desglose matemático de medidas y pesos.
[ACTION - RECOMENDACIÓN TÉCNICA] Pasos operativos + DRAFT SUGERIDO (Texto exacto para documentos).
[ESTÁNDAR DE ACEPTACIÓN] Qué revisará el counter/autoridad y cómo cumplir.
[WHY - IMPACTO OPERATIVO] Riesgos de multas y retrasos ante el gobierno si no se sigue la recomendación.
[CLOSE] Movimiento final del asesor.

Idioma: {lang}. Rol: {role}.
ENTRADA DEL USUARIO: {prompt}
"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json={
                "contents": [{"parts": [{"text": system_instruction}]}],
                "generationConfig": {
                    "temperature": 0.1, # Máxima precisión técnica
                    "maxOutputTokens": 2048
                }
            })
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"data": text}
    except Exception as e:
        logger.error(f"Error en el asesor: {e}")
        return {"data": "El sistema SmartCargo experimenta una demora técnica. Reintente."}

# ================= ENDPOINTS DE APOYO =================
@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    logger.info(f"Reporte enviado a: {email}")
    return {"status": "success"}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Asesoría SmartCargo {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/"
        )
        return {"url": session.url}
    except: return JSONResponse({"error": "Error"}, status_code=400)
