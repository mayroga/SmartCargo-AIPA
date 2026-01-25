from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.rules import validate_cargo  # tu módulo backend

app = FastAPI(title="SmartCargo-AIPA · Asesor documental")

# Monta la carpeta 'static' (JS/CSS) desde la raíz
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta principal que sirve el index.html desde frontend/
@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")  # <-- ruta correcta
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
    cargos = []  # Aquí puedes reemplazar con tus cargos reales
    return JSONResponse(cargos)
