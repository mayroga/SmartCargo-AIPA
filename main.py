import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI()

# Configuración de CORS Totalmente Abierta para evitar bloqueos en Render/Mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la API Key (Asegúrate de ponerla en los Environment Variables de Render)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """
Eres 'SmartCargo-AIPA', Maestro Logístico de Avianca. 
DOMINAS: IATA, DOT, CBP, TSA y toda la papelería (AWB, MAWB, HAWB, SLI, CBP 7509, etc.).
TAREAS: 
1. Si el operador describe carga o documentos, da soluciones técnicas.
2. Si pide 'Clear Doubts', profundiza en la explicación legal y operativa.
3. Sugiere Prioridad (Must-Go, General, Stand-by) y ULD (PMC/AKE).
4. Asesora sobre el balanceo en A330F/767 para ahorro de combustible.
5. Si no hay descripción visual, solicita detalles al operador.
LEGAL: Usa lenguaje asesor ('Sugerencia técnica'). No eres autoridad.
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Error: index.html no encontrado."

@app.post("/advisory")
async def process_advisory(
    prompt: str = Form(...), 
    awb: str = Form(...),
    l: str = Form(""), w: str = Form(""), h: str = Form(""),
    pcs: str = Form(""), wgt: str = Form(""), unit: str = Form("")
):
    try:
        # Construcción del contexto técnico
        cargo_data = f"AWB: {awb} | Dims: {l}x{w}x{h} {unit} | Pcs: {pcs} | Wgt: {wgt}"
        full_context = f"{SYSTEM_PROMPT}\n\nDATOS CARGA: {cargo_data}\nREPORTE OPERADOR: {prompt}\n\nSOLUCIÓN TÉCNICA:"
        
        response = model.generate_content(full_context)
        return JSONResponse(content={"data": response.text})
    except Exception as e:
        return JSONResponse(content={"data": f"Error de conexión con AIPA Hub: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
