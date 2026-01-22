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

# Inicialización con el Core de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Instrucciones de Peso y Blindaje Legal
SYSTEM_PROMPT = """
Eres la Asesora Especialista SmartCargo by May Roga. 
TU ESTILO: Específica, técnica, pocas palabras pero con mucho peso.
FORMATO: Usa tablas Markdown con espacio generoso. Si piden un documento (AWB, Manifiesto, etc.), simúlalo en una caja de texto técnica.
LEGAL: NO menciones nombres de agencias gubernamentales o regulatorias (IATA, DOT, CBP). Usa términos como 'Protocolo de Seguridad', 'Norma Técnica' o 'Requisito de Aduana'. 
TU MISIÓN: Resolver, clasificar carga (FullPallet, BUP, etc.), calcular volumen (1:6) y prever rechazos en rampa.
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
    lang_msg = "Respond in Spanish." if lang == "es" else "Respond in English."
    full_context = f"{lang_msg}\nDATA: AWB {awb} | Dims: {l}x{w}x{h} | Pcs: {pcs} | Wgt: {wgt}\nUSER REQUEST: {prompt}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": full_context}],
            temperature=0.2 # Máxima precisión técnica
        )
        return JSONResponse(content={"data": response.choices[0].message.content})
    except:
        return JSONResponse(content={"data": "System Error / Error de Comunicación Core."}, status_code=500)
