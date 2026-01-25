# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.rules import validate_cargo  # tu función de validación en backend/rules.py
import os

app = FastAPI(title="Asesor SmartCargo-AIPA")

# Montar archivos estáticos desde la carpeta 'static' en la raíz
if not os.path.exists("static"):
    raise RuntimeError("No se encontró la carpeta 'static' en la raíz del proyecto")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates apuntando a la carpeta 'frontend'
if not os.path.exists("frontend/index.html"):
    raise RuntimeError("No se encontró 'index.html' en la carpeta 'frontend'")
templates = Jinja2Templates(directory="frontend")

# Página principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint para listar todos los documentos (demo)
@app.get("/cargo/list_all")
async def list_all_cargo():
    # Ejemplo de datos
    return {
        "total": 128,
        "correct": 94,
        "warning": 21,
        "critical": 13,
        "documents": [
            {"AWB": "134-98765432", "Documento": "Air Waybill", "Estado": "Aprobado", "Observación": "Sin inconsistencias", "Norma": "IATA TACT"},
            {"AWB": "134-12345678", "Documento": "Factura Comercial", "Estado": "Observación", "Observación": "Valor declarado incompleto", "Norma": "Aduana"},
            {"AWB": "134-45678901", "Documento": "Lista de Empaque", "Estado": "Crítico", "Observación": "Falta firma del exportador", "Norma": "IATA / ICAO"},
        ]
    }

# Endpoint para validar documentos usando rules.py
@app.post("/cargo/validate")
async def validate_cargo_endpoint(data: dict):
    try:
        result = validate_cargo(data)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# Health check simple
@app.get("/health")
async def health():
    return {"status": "ok"}
