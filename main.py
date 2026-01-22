import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI(title="SmartCargo-AIPA by MAY ROGA LLC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uso de GEMINI_API_KEY según tu configuración
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Protocolo Maestro con toda la papelería de Miami/Avianca
SYSTEM_PROMPT = """
Eres 'SmartCargo-AIPA', el Asesor Maestro de Avianca Cargo en Miami. 
Tu conocimiento incluye TODA la papelería técnica y de warehouse:

DOCUMENTOS DE TRANSPORTE: AWB, HAWB, MAWB, B/L, SLI, Cargo Manifest, Pre-Alert.
ADUANAS Y LEGAL: Commercial Invoice, Packing List, Certificado de Origen, Export/Import License, CBP 7509, Customs Entry.
SEGURIDAD Y DG: Dangerous Goods Declaration, Security Risk Assessment, Handling Labels.
INTERNOS WAREHOUSE: Warehouse Receipt, Cargo Check-In Sheets, Inventory Control, Temperature/Cold Chain Logs, Damage/Discrepancy Reports, Pick/Pack Lists, Equipment Maintenance Logs.

TU MISIÓN:
1. Si el usuario menciona un documento, recita sus campos obligatorios y su función.
2. Si hay discrepancias (Damage Report), guía al usuario en el proceso de reporte.
3. Si el usuario "no sabe", actúa como MAESTRO EMERGENTE: da una lección técnica rápida.
4. Calcula Profit (1:6) y sugiere ULD (PMC/AKE) y posición en A330F o 767 para balanceo (CoG).

LEGAL: Lenguaje de asesoría ('Se recomienda', 'Sugerencia técnica'). No eres gobierno ni autoridad.
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/advisory")
async def process_advisory(
    prompt: str = Form(...), 
    awb: str = Form(...), 
    lang: str = Form(...),
    l: str = Form(None), w: str = Form(None), h: str = Form(None),
    pcs: str = Form(None), wgt: str = Form(None), unit: str = Form(None)
):
    # Estructura de datos para la IA
    tech_data = f"AWB: {awb} | Dimensiones: {l}x{w}x{h} {unit} | Piezas: {pcs} | Peso: {wgt}"
    
    # Si no hay descripción de foto, la IA solicitará detalles basándose en este prompt
    context = f"{SYSTEM_PROMPT}\nIdioma: {lang}\nDatos Técnicos: {tech_data}\nDescripción del Operador: {prompt}\n\nSOLUCIÓN TÉCNICA:"

    try:
        response = model.generate_content(context)
        return {"data": response.text}
    except Exception:
        # Fallback si Gemini falla (aquí podrías conectar OpenAI si tienes la Key)
        return {"data": "AIPA Hub fuera de línea. Por favor, proceda con revisión manual de Warehouse Check-In Sheets y reporte de discrepancias."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
