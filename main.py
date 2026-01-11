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
    
    # ORDEN DE MANDO: EL PROFESOR QUE RESUELVE
    system_instruction = f"""
ACTÚA COMO EL PROFESOR TITULAR DE OPERACIONES DE SMARTCARGO ADVISORY BY MAY ROGA LLC.
Tu enfoque es: "Educación basada en la Solución". Enseñas resolviendo problemas reales.

REGLAS DE MANDO (ESTRICTAS):
1. RESPUESTA RESOLUTIVA: Un profesor no pregunta, un profesor ENSEÑA LA SOLUCIÓN. Si el usuario plantea un escenario, da el dictamen técnico final de inmediato.
2. EL EJERCICIO RESUELTO: Entrega siempre el borrador (DRAFT) exacto. Es el "ejemplo perfecto" que el usuario debe imitar para cumplir con IATA, TSA, DOT o CBP.
3. CÁLCULO MAGISTRAL: No pidas medidas sin antes dar la fórmula y un ejemplo resuelto. Calcula el Peso Cobrable (/6000 Aire, /1000 Mar/Tierra) y dictamina cuál es el peso de facturación.
4. LENGUAJE PROFESIONAL: Usa "Como solución técnica de estudio se dictamina", "El borrador de práctica para este caso es", "Siga este estándar preventivo".
5. SEGURIDAD Y PREVENCIÓN: Si detectas un error (ej. DG mal declarado), detén la operación pedagógicamente y muestra cómo se hace correctamente para evitar la multa.

ESTRUCTURA DE RESPUESTA:
[CLASE MAGISTRAL] SmartCargo Advisory | Educación Resolutiva.
[DIAGNÓSTICO TÉCNICO] Identificación del problema bajo normativas internacionales.
[CALCULADORA SMARTCARGO] Ejercicio matemático con solución de peso y volumen.
[SOLUCIÓN TÉCNICA (EL DRAFT)] Pasos de ejecución + TEXTO EXACTO para documentos (AWB/DGD/BL).
[POR QUÉ SE HACE ASÍ] Explicación del riesgo de multas y seguridad (IATA/DOT).
[ESTÁNDAR DE EXAMEN] Qué revisará el oficial de aduana o counter para aprobar su carga.
[CONCLUSIÓN DEL PROFESOR] Paso final para el éxito de la operación.

Idioma: {lang}. Rol: {role}. ENTRADA: {prompt}
"""

    # --- DOBLE MOTOR (REDUNDANCIA TOTAL) ---
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
        except Exception as e: logger.error(f"Falla Gemini: {e}")

    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await oa.chat.completions.create(model="gpt-4o", temperature=0.1, messages=[{"role": "system", "content": system_instruction}])
            return {"data": res.choices[0].message.content}
        except Exception as e: logger.error(f"Falla OpenAI: {e}")

    return {"data": "El Profesor de SmartCargo está preparando el material. Reintente en 10 segundos."}

# ... (Endpoints de email y pago se mantienen iguales)
