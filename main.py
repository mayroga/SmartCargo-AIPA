import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI()

# CORRECCIÓN DE CORS: Permite comunicación total sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Inteligencia
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Protocolo con la lista de documentos que proporcionaste
SYSTEM_PROMPT = """
Eres 'SmartCargo-AIPA', Asesor Maestro de Avianca Cargo.
DOMINAS TODA LA PAPELERÍA: AWB, HAWB, MAWB, B/L, Commercial Invoice, Packing List, SLI, Cargo Manifest, Certificate of Origin, DGD, CBP 7509, Warehouse Receipt, etc.
INSTRUCCIONES:
1. Si el operador no conoce un documento o proceso, actúa como maestro y explica.
2. Calcula peso volumétrico (1:6). Sugiere ULD (PMC/AKE) y flota (A330F/767).
3. Sugiere prioridad: Must-Go, General o Stand-by.
4. Si la descripción es por voz/texto, analízala con rigor técnico.
5. No uses 'IA' o 'Gobierno'. Usa: 'Recomendación Técnica de SmartCargo'.
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/advisory")
async def advisory_endpoint(
    prompt: str = Form(...),
    awb: str = Form(""),
    l: str = Form(""), w: str = Form(""), h: str = Form(""),
    pcs: str = Form(""), wgt: str = Form(""), unit: str = Form("")
):
    try:
        # Unión de datos para el análisis
        context = f"DATOS: AWB {awb}, Dim {l}x{w}x{h} {unit}, Cant {pcs}, Peso {wgt}.\nDESCRIPCIÓN: {prompt}"
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\n{context}")
        return JSONResponse(content={"data": response.text})
    except Exception as e:
        return JSONResponse(content={"data": f"Error del sistema: {str(e)}"}, status_code=500)
