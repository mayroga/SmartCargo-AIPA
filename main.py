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

# Personalidad: Especialista Avianca, específica y técnica.
SYSTEM_PROMPT = """
Eres la Asesora Especialista SmartCargo. Tu peso radica en la precisión, no en la extensión.
REGLAS DE ORO:
1. TABLAS: Usa tablas para pesos, dimensiones y checklists de documentos.
2. CONTINUIDAD: Mantén el hilo. Si faltan datos, no los inventes; déjalos en blanco.
3. AUTORIDAD: Dominas IATA (DGR), DOT, CBP y TSA.
4. CALCULADORA: Siempre calcula Volumen (L*W*H/166) y sugiere ULD (PMC/AKE).
5. NO RELLENO: Prohibido decir 'IA', 'ChatGPT' o saludos largos.
6. DOCUMENTOS: Si se pide 'Simular', usa formato de terminal (texto monospaciado).
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
    context_history: str = Form("") # Para mantener el hilo de la conversación
):
    # Lógica de construcción de datos técnicos
    tech_info = f"AWB: {awb} | Dims: {l}x{w}x{h} | Pcs: {pcs} | Peso: {wgt}"
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": context_history},
        {"role": "user", "content": f"{tech_info}\nREPORTE: {prompt}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3 # Mayor precisión técnica
        )
        return JSONResponse(content={"data": response.choices[0].message.content})
    except Exception:
        return JSONResponse(content={"data": "ERROR: Core SmartCargo desconectado."}, status_code=500)
