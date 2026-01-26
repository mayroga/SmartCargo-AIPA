import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="SMARTCARGO-AIPA BY MAY ROGA LLC")

# Habilitar CORS para evitar bloqueos de navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Rutas Estáticas
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def asesor_experto_logistica(prompt: str) -> str:
    """Motor de validación técnica sin mención a modelos externos."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "ERROR CRÍTICO: El sistema de validación no está disponible. Contacte a soporte de SMARTCARGO-AIPA."

@app.get("/")
async def serve_frontend():
    index_path = BASE_DIR / "frontend" / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Archivo index.html no encontrado en /frontend")
    return FileResponse(index_path)

@app.post("/validate")
async def validate_cargo(
    mawb: str = Form(...),
    role: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    length: float = Form(...),
    width: float = Form(...),
    lang: str = Form("en")
):
    # Reglas de Negocio Avianca / DOT / IATA
    volume = round((length * width * height) / 1000000, 3)
    
    # Prompt de alta especificidad técnica
    prompt = f"""
    Actúa como SMARTCARGO-AIPA. Experto en IATA DGR, TSA, CBP y DOT.
    Analiza esta carga para transporte en AVIANCA (Carguero y Pasajeros).
    
    DATOS:
    - Rol: {role}
    - MAWB: {mawb}
    - Mercancía: {cargo_type}
    - Peso: {weight} kg
    - Dimensiones: {length}x{width}x{height} cm
    - Volumen: {volume} m3
    
    INSTRUCCIONES:
    1. Usa una TABLA para comparar estas dimensiones con los límites de bodega de un A320 (Belly) vs A330F.
    2. Si es DG, cita la necesidad de Shipper's Declaration según IATA.
    3. Idioma: {lang}. Tono: Profesional, corto, de mucho peso.
    4. NO menciones IA. No menciones ser un modelo de lenguaje.
    """

    analisis = asesor_experto_logistica(prompt)
    
    # Lógica de Semáforo
    status = "GREEN"
    if height > 160 or weight > 4000:
        status = "RED"
    elif cargo_type.upper() in ["DG", "HAZMAT"]:
        status = "YELLOW"

    return JSONResponse({
        "status": status,
        "analysis": analisis,
        "legal": "SMARTCARGO-AIPA BY MAY ROGA LLC: SISTEMA DE ASESORÍA PREVENTIVA. EL USO DE ESTA HERRAMIENTA NO EXIME DEL CUMPLIMIENTO DE LAS REGULACIONES DEL DOT, TSA Y LAS POLÍTICAS DE AVIANCA CARGO."
    })
