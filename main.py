from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.rules import validate_cargo  # Asegúrate de que rules.py existe
from typing import Optional

app = FastAPI(title="Asesor SmartCargo-AIPA")

# Monta la carpeta de archivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Configura Jinja2 para templates
templates = Jinja2Templates(directory="frontend")

# Endpoint principal que sirve index.html
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint para listar todos los cargos (simulación)
@app.get("/cargo/list_all")
async def list_all_cargo():
    # Ejemplo de datos de prueba
    cargo_list = [
        {"awb": "134-98765432", "document": "Air Waybill", "status": "Aprobado", "observation": "Sin inconsistencias", "norm": "IATA TACT"},
        {"awb": "134-12345678", "document": "Factura Comercial", "status": "Observación", "observation": "Valor declarado incompleto", "norm": "Aduana"},
        {"awb": "134-45678901", "document": "Lista de Empaque", "status": "Crítico", "observation": "Falta firma del exportador", "norm": "IATA / ICAO"}
    ]
    return JSONResponse(content=cargo_list)

# Endpoint para validar cargo
@app.post("/cargo/validate")
async def validate(
    mawb: str = Form(...),
    hawb: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...)
):
    try:
        # Llama a tu función de validación del módulo rules.py
        result = validate_cargo(mawb, hawb, origin, destination, cargo_type, flight_date)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# Para depuración rápida
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
