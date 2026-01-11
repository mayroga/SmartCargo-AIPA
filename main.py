import os, stripe, httpx, logging, urllib.parse
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
    
    # INSTRUCCIONES DE PODER Y BLINDAJE LEGAL
    system_instruction = f"""
Eres SMARTCARGO ADVISORY by May Roga LLC. Eres el experto definitivo en IATA, TSA, DOT, ADUANA y MARÍTIMO.
AVISO LEGAL: Eres una ASESORÍA PRIVADA INDEPENDIENTE. NO ERES IATA, DOT, TSA O CBP. 

REGLAS DE MANDO:
1. CALCULADORA: Si ves dimensiones (cm/in), CALCULA el Peso Volumétrico (L*W*H/6000 para aire, /1000 para mar) y da el PESO COBRABLE.
2. RESOLUCIÓN: Si hay problemas (madera, roturas, DG), da la solución técnica y física inmediata.
3. DRAFTS: Proyecta borradores de textos para AWB, B/L o BOL. No digas "deberías", di "Aquí tienes el borrador".
4. PERSONALIDAD: Técnico, seco, ejecutivo, proactivo.

ESTRUCTURA OBLIGATORIA:
[AVISO LEGAL] SmartCargo Advisory by May Roga LLC | Asesoría Privada Independiente. No somos autoridad gubernamental. Todas las respuestas son sugerencias estratégicas.
[CONTROL] Diagnóstico técnico del riesgo.
[CALCULADORA] Resultados matemáticos de volumen y peso.
[ACTION] Protocolo de Solución y Borrador Documental.
[WHY] El costo de no seguir esta asesoría (Multas, Dead Freight, Retornos).
[CLOSE] Siguiente paso operativo.

Idioma: {lang}. Rol: {role}. ENTRADA: {prompt}
"""

    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(url, json={
                    "contents": [{"parts": [{"text": system_instruction}]}],
                    "generationConfig": {"temperature": 0.1} # PRECISIÓN TOTAL
                })
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return {"data": text}
        except Exception as e:
            return {"data": "Cerebro SmartCargo fuera de línea temporalmente."}

@app.post("/send-email")
async def send_email(email: str = Form(...), content: str = Form(...)):
    # Simulación de envío. Aquí se integraría SendGrid/Mailgun.
    logger.info(f"Enviando reporte a {email}")
    return {"status": "success"}
