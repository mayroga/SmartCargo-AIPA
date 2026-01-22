import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

# Configuración de CORS total para evitar bloqueos en rampa
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización exclusiva con OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Eres 'SmartCargo-AIPA', el Asesor Maestro de Carga de Avianca Cargo.
CONOCIMIENTO EXPERTO: IATA DGR, DOT, CBP, TSA y toda la papelería técnica (AWB, HAWB, MAWB, SLI, CBP 7509, DGD, Warehouse Receipt, etc.).

PROTOCOLO OPERATIVO:
1. DOCUMENTACIÓN: Si el usuario menciona o describe un documento, recita sus campos obligatorios y verifica su validez técnica.
2. MAESTRO EMERGENTE: Si el operador tiene dudas, da una lección técnica directa y profesional.
3. LOGÍSTICA: Calcula pesos volumétricos (1:6), sugiere ULD (PMC/AKE) y flota (A330F/767).
4. PRIORIZACIÓN: Clasifica en Must-Go, General o Stand-by.
5. ACLARAR DUDAS: Si se activa el modo VIP, profundiza en la explicación pedagógica y legal.

IMPORTANTE: No uses las palabras 'IA', 'Inteligencia Artificial' ni 'Gobierno'. Eres un Asesor Estratégico Privado.
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
    pcs: str = Form(""), wgt: str = Form(""), unit: str = Form(""),
    clear_doubts: str = Form("false")
):
    # Consolidación de datos técnicos para OpenAI
    full_context = f"DATOS TÉCNICOS: AWB/ULD: {awb} | Dims: {l}x{w}x{h} {unit} | Pcs: {pcs} | Peso: {wgt}\n"
    full_context += f"REPORTE DEL OPERADOR: {prompt}\n"
    full_context += f"MODO ACLARAR DUDAS: {clear_doubts}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_context}
            ],
            temperature=0.7
        )
        return JSONResponse(content={
            "data": response.choices[0].message.content, 
            "source": "SmartCargo Core (OpenAI GPT-4o)"
        })
    except Exception as e:
        return JSONResponse(content={"data": f"Error de conexión con el Core: {str(e)}"}, status_code=500)
