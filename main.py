import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Eres la Asesora Especialista SmartCargo by May Roga. 
ESTILO: Específica, técnica, de pocas palabras pero con mucho peso.
FORMATO: Tablas claras con mucho espacio.
LEGAL: Actúa como consultora técnica. NO menciones ser autoridad ni nombres instituciones regulatorias directamente para evitar multas o demandas. Usa términos como 'Protocolo de Seguridad', 'Requisito de Aduana' o 'Norma de Transporte'.
OBJETIVO: Resolver discrepancias, calcular volumen y asegurar que la carga llegue lista para el counter.
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/advisory")
async def process_advisory(
    prompt: str = Form(...), 
    awb: str = Form(""),
    l: str = Form(""), w: str = Form(""), h: str = Form(""),
    pcs: str = Form(""), wgt: str = Form(""),
    lang: str = Form("en")
):
    lang_instruction = "Respond ALWAYS in Spanish." if lang == "es" else "Respond ALWAYS in English."
    full_context = f"{lang_instruction}\nDATA: AWB {awb} | Dims: {l}x{w}x{h} | Pcs: {pcs} | Wgt: {wgt}\nUSER: {prompt}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": full_context}]
        )
        return JSONResponse(content={"data": response.choices[0].message.content})
    except:
        return JSONResponse(content={"data": "System Error / Error de Sistema"}, status_code=500)
