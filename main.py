import os, httpx, logging, urllib.parse
from fastapi import FastAPI, Form
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

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), role: Optional[str] = Form("auto")):
    system_instruction = f"""
Eres SMARTCARGO ADVISORY by May Roga LLC. Eres el experto táctico en logística.
AVISO LEGAL: ASESORÍA PRIVADA INDEPENDIENTE. NO SOMOS IATA, DOT, TSA O CBP.

REGLAS DE MANDO:
1. CÁLCULO: Si hay medidas, calcula Volumen y Peso Cobrable (Aéreo /6000, Marítimo /1000).
2. RESOLUCIÓN: Si hay problemas (Madera, DG, Daños), da la solución técnica física.
3. DRAFTS: Proyecta borradores de texto para AWB/BL/BOL.
4. LENGUAJE: Eres un experto. Habla con autoridad técnica pero como asesor privado.

ESTRUCTURA:
[AVISO LEGAL] SmartCargo Advisory by May Roga LLC | Asesoría Privada Independiente.
[CONTROL] Diagnóstico experto.
[CALCULADORA SMARTCARGO] Resultados matemáticos.
[ACTION - SOLUCIÓN] Protocolo técnico + Draft del documento.
[ESTÁNDAR DE COUNTER] Lo que el inspector rechazará si no corriges.
[WHY] El costo real (Multas, Dead Freight).
[CLOSE] Siguiente paso operativo.

Idioma: {lang}. Rol: {role}. ENTRADA: {prompt}
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json={
                "contents": [{"parts": [{"text": system_instruction}]}],
                "generationConfig": {"temperature": 0.1}
            })
            return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
    except Exception as e:
        return {"data": "Cerebro en calibración. Intente de nuevo."}

@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    logger.info(f"Enviando reporte a {email}")
    return {"status": "success"}
