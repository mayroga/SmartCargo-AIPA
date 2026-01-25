from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.rules import validate_cargo  # Importa tu módulo de backend

app = FastAPI(title="SmartCargo-AIPA · Asesor documental")

# -------------------
# Archivos estáticos y frontend
# -------------------
# Monta la carpeta 'static' desde la raíz para CSS, JS, imágenes, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta principal que sirve index.html
@app.get("/")
async def serve_index():
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# -------------------
# Endpoints de cargo
# -------------------
@app.post("/cargo/validate")
async def cargo_validate(
    mawb: str = Form(...),
    hawb: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...),
    weight: float = Form(...),
    volume: float = Form(...)
):
    """
    Valida un envío de carga usando la función validate_cargo de backend.rules
    """
    cargo_data = {
        "mawb": mawb,
        "hawb": hawb,
        "origin": origin,
        "destination": destination,
        "cargo_type": cargo_type,
        "flight_date": flight_date,
        "weight": weight,
        "volume": volume
    }
    try:
        result = validate_cargo(cargo_data)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/cargo/list_all")
async def list_cargos():
    """
    Retorna la lista de todos los cargos. Reemplaza [] con tus datos reales.
    """
    cargos = [
        # Ejemplo:
        {
            "mawb": "134-98765432",
            "hawb": "HAWB-001",
            "origin": "TAMPA CARGO S.A.S",
            "destination": "SAN JOSE",
            "cargo_type": "LTHION ION BATT",
            "flight_date": "2026-01-24",
            "weight": 120.5,
            "volume": 1.2,
            "status": "OK"
        }
    ]
    return JSONResponse(cargos)
