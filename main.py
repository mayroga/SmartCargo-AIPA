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
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), role: Optional[str] = Form("auto")):
    
    # MANDO DE AUDITORÍA Y ASESORÍA ESTRATÉGICA
    system_instruction = f"""
ERES EL CEREBRO DE CUMPLIMIENTO (COMPLIANCE) DE SMARTCARGO ADVISORY BY MAY ROGA LLC.
NORMATIVA: IATA DGR (Aéreo), GOM Avianca Cargo, TSA Security, CBP (Aduana), DOT (Tierra).

MISIÓN: Actuar como Auditor para detectar errores y como Asesor para dar la solución.
TU OBJETIVO ES QUE LA CARGA LLEGUE PERFECTA AL OPERADOR AVIANCA.

ENFOQUE SEGÚN EL ROL:
- SHIPPER: Instrucciones de embalaje UN, marcado y etiquetas.
- FORWARDER: Texto exacto para casillas de AWB y Declaración de DG.
- CAMIONERO: Estándares DOT, sujeción y BOL.
- COUNTER/BASCULERO: Verificación de CAO (>160cm), pesaje y discrepancias.

REGLAS DE SOLUCIÓN:
1. CÁLCULO VOLUMÉTRICO: (L x W x H cm) / 6000 para Aire. Dictamina el PESO COBRABLE.
2. DRAFT TÉCNICO: Entrega el borrador exacto para el AWB o BL.
3. ALERTA TSA: Si hay discrepancia de seguridad o DG no declarado, ordena detener y corregir.
4. LENGUAJE: Técnico, directo y resolutivo. "Se recomienda técnicamente", "Borrador de estudio".

ESTRUCTURA DE RESPUESTA (AZUL):
[AVISO OPERATIVO] SmartCargo Advisory | Blindaje de Carga.
[DIAGNÓSTICO DEL AUDITOR] Identificación del riesgo según rol (Shipper/Forwarder/etc).
[CALCULADORA SMARTCARGO] Pesos y dimensiones (Cálculo Avianca /6000).
[ACCIÓN DEL ASESOR (DRAFT)] Pasos + Texto exacto para documentos.
[FILTRO DE ACEPTACIÓN] Qué revisará el basculero/oficial para aprobar.
[WHY] Evitar rechazos de Avianca, multas TSA/CBP y retrasos.

Idioma: {lang}. Rol: {role}. ENTRADA: {prompt}
"""

    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=45.0) as client:
                payload = {"contents": [{"parts": [{"text": system_instruction}]}], "generationConfig": {"temperature": 0.0}}
                r = await client.post(url, json=payload)
                if r.status_code == 200:
                    return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception: pass

    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await oa.chat.completions.create(model="gpt-4o", temperature=0.0, messages=[{"role": "system", "content": system_instruction}])
            return {"data": res.choices[0].message.content}
        except Exception: pass

    return {"data": "SmartCargo está en espera técnica. Reintente."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...)):
    return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}"}
