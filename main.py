from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.rules import validate_cargo

app = FastAPI(title="SmartCargo-AIPA · Asesor documental aeronáutico")

# Carpeta para CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Carpeta para HTML
templates = Jinja2Templates(directory="templates")

# -------------------
# Ruta principal
# -------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------
# Validar cargo
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

    result = validate_cargo(cargo_data)
    return result

# -------------------
# Listar todos los cargos
# -------------------
@app.get("/cargo/list_all")
async def list_cargos():
    # Aquí podrías leer de DB o mock data
    return []  # Reemplaza con tus cargos
