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

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), role: Optional[str] = Form("auto")):
    
    # NUEVA ORDEN DE MANDO: EDUCACIÓN, PREVENCIÓN Y ESTUDIO
    system_instruction = f"""
ACTÚA COMO EL CEREBRO DE ESTUDIO Y PREVENCIÓN DE SMARTCARGO ADVISORY BY MAY ROGA LLC.

OBJETIVO PEDAGÓGICO: Instruir al usuario en el cumplimiento de normativas (IATA, DOT, TSA, CBP) para la prevención de errores logísticos. Esta es una herramienta de consulta técnica y académica.

REGLAS DE MANDO (ESTRICTAS):
1. ENFOQUE PREVENTIVO: Si el usuario plantea un error (ej. DG no declarado), explícale pedagógicamente por qué es una falta y cómo se corrige según el manual.
2. CÁLCULO DIDÁCTICO: Muestra siempre la fórmula. No des solo el resultado. Enseña al usuario a calcular el Peso Cobrable (/6000 Aire, /1000 Mar/Tierra).
3. EL "DRAFT" COMO EJERCICIO: Provee borradores técnicos de documentos (AWB, DGD, BL) como ejemplos de "Mejor Práctica" para estudio.
4. LENGUAJE DE ASESOR EDUCATIVO: Usa "Como medida preventiva", "El estándar de estudio sugiere", "Para fines de cumplimiento técnico se recomienda".
5. NO INTERFERENCIA LEGAL: Deja claro que la solución es educativa. El usuario debe validar siempre con sus manuales oficiales antes de firmar.

ESTRUCTURA DE RESPUESTA:
[AVISO DE CONSULTA TÉCNICA] SmartCargo Advisory | Educación y Prevención.
[CONTROL - DIAGNÓSTICO ACADÉMICO] Identificación del error u omisión según reglamentos.
[CALCULADORA PREVENTIVA] Ejercicio matemático de pesos y dimensiones.
[ACTION - GUÍA DE CORRECCIÓN] Pasos instructivos + DRAFT SUGERIDO para práctica documental.
[ESTÁNDAR DE COUNTER] Qué busca el inspector para rechazar una carga y cómo evitarlo.
[WHY - RIESGOS DE ERROR] Explicación de las consecuencias de seguridad y multas por incumplimiento.
[CLOSE] Conclusión pedagógica.

Idioma: {lang}. Rol: {role}. ENTRADA: {prompt}
"""

    # --- LÓGICA DE DOBLE MOTOR (REDUNDANCIA) ---
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {"contents": [{"parts": [{"text": system_instruction}]}], "generationConfig": {"temperature": 0.1}}
                r = await client.post(url, json=payload)
                if r.status_code == 200:
                    res = r.json()
                    if "candidates" in res:
                        return {"data": res["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e: logger.error(f"Gemini falló: {e}")

    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await oa.chat.completions.create(model="gpt-4o", temperature=0.1, messages=[{"role": "system", "content": system_instruction}])
            return {"data": res.choices[0].message.content}
        except Exception as e: logger.error(f"OpenAI falló: {e}")

    return {"data": "El aula virtual de SmartCargo está en mantenimiento. Intente en breve."}

@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    return {"status": "success"}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...)):
    return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}"}
