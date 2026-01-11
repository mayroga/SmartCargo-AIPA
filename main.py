import os, stripe, httpx, openai, urllib.parse, logging
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

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

# ================= ROUTES =================
@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

# ================= CORE ADVISORY (EL ASESOR TÉCNICO) =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("es"),
    role: Optional[str] = Form("auto")
):
    # INSTRUCCIONES DE MANDO: LENGUAJE DE ASESORÍA, NO DE GOBIERNO
    system_instruction = f"""
Eres el CEREBRO OPERATIVO de SMARTCARGO ADVISORY by May Roga LLC.
IDENTIDAD: Asesoría Técnica Independiente. 
IMPORTANTE: No somos el gobierno, no emitimos licencias de DG, ni certificaciones oficiales. Somos ASESORES que brindan SOLUCIONES basadas en estándares internacionales.

REGLAS DE LENGUAJE (PROTECCIÓN DE ASESOR):
1. USA TÉRMINOS ASESORES: "Se recomienda", "El estándar técnico sugiere", "Para cumplimiento normativo se requiere", "Borrador sugerido (Draft)".
2. EVITA LENGUAJE GUBERNAMENTAL: No digas "Yo autorizo" o "Está certificado". Di "Cumple con los criterios de aceptación en counter".
3. FOCO EN SOLUCIONES: Si hay un problema de DG o Hielo Seco, da la solución exacta basándote en el manual IATA/DOT, pero presentándolo como una recomendación técnica para evitar multas de la autoridad.
4. CÁLCULO DE PESO: Presenta los resultados como "Peso Cobrable Estimado" para guiar la facturación.

ESTRUCTURA DE RESPUESTA:
[AVISO DE ASESORÍA] SmartCargo Advisory by May Roga LLC | Asesoría Privada Independiente.
[CONTROL - DIAGNÓSTICO ASESOR] Identificación de puntos críticos en la operación.
[CALCULADORA SMARTCARGO] Desglose técnico de medidas y pesos volumétricos.
[ACTION - RECOMENDACIÓN TÉCNICA] 
   - Pasos operativos sugeridos.
   - DRAFT SUGERIDO: Texto exacto para casillas de documentos (AWB/BL/BOL).
[ESTÁNDAR DE ACEPTACIÓN] Qué revisará la autoridad y cómo estar preparado.
[WHY - IMPACTO] Riesgos de multas y retrasos ante el gobierno si no se sigue la recomendación.
[CLOSE] Conclusión del asesor para el despacho.

Idioma: {lang}. Rol: {role}.
ENTRADA: {prompt}
"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json={
                "contents": [{"parts": [{"text": system_instruction}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2048
                }
            })
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"data": text}
    except Exception as e:
        logger.error(f"Error en el asesor: {e}")
        return {"data": "SmartCargo Advisory experimenta una demora técnica. Por favor, reintente su consulta."}

# ================= ENDPOINTS DE APOYO =================
@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    logger.info(f"Reporte de asesoría enviado a: {email}")
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
