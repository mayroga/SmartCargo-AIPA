import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from openai import OpenAI

app = FastAPI()

# Configuración de CORS total para evitar bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización de Claves
api_key_gemini = os.environ.get("GEMINI_API_KEY")
api_key_openai = os.environ.get("OPENAI_API_KEY")

client_openai = OpenAI(api_key=api_key_openai)

SYSTEM_PROMPT = """
Eres 'SmartCargo-AIPA', Asesor Maestro de Avianca Cargo.
DOMINAS: IATA, DOT, CBP, TSA y toda la papelería de warehouse (AWB, SLI, CBP 7509, DGR).
TAREAS: 
1. Si el operador tiene dudas de documentos, explica como maestro.
2. Calcula peso volumétrico (1:6) y sugiere ULD (PMC/AKE) y flota (A330F/767).
3. Prioriza: Must-Go, General o Stand-by.
4. Resuelve dudas VIP con detalle pedagógico.
No uses 'IA' ni 'Gobierno'. Usa 'Asesoría Técnica de SmartCargo'.
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
    full_context = f"{SYSTEM_PROMPT}\n\nDATOS: AWB {awb}, Dim {l}x{w}x{h}, Pcs {pcs}, Wgt {wgt}\nREPORTE: {prompt}\nVIP MODE: {clear_doubts}"
    
    # --- INTENTO 1: GEMINI ---
    try:
        genai.configure(api_key=api_key_gemini)
        model_gemini = genai.GenerativeModel('gemini-1.5-flash')
        response = model_gemini.generate_content(full_context)
        return JSONResponse(content={"data": response.text, "source": "AIPA-Flash (Gemini)"})
    
    except Exception as e:
        # --- INTENTO 2: RESPALDO AUTOMÁTICO CON OPENAI ---
        try:
            response = client_openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": full_context}]
            )
            return JSONResponse(content={
                "data": response.choices[0].message.content, 
                "source": "AIPA-SafeMode (OpenAI Backup)"
            })
        except Exception as e2:
            return JSONResponse(content={"data": "Error crítico: Ambos sistemas fuera de línea. Verifique API Keys."}, status_code=500)
