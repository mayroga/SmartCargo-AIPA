from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from backend.rules import validate_cargo
import os

app = FastAPI(title="Asesor SmartCargo-AIPA")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta /static para JS, CSS
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================
# MODELOS DE DATOS
# ==========================
class Document(BaseModel):
    doc_type: str
    observation: Optional[str] = ""
    norm: Optional[str] = "IATA"
    expired: Optional[bool] = False

class Cargo(BaseModel):
    mawb: str
    hawb: str
    origin: str
    destination: str
    cargo_type: str
    flight_date: str
    weight: Optional[float] = 0
    volume: Optional[float] = 0
    documents: Optional[List[Document]] = []

# ==========================
# BASE DE DATOS SIMULADA
# ==========================
CARGOS_DB: List[Cargo] = []

# ==========================
# ENDPOINTS
# ==========================

# Servir index.html
@app.get("/")
def root():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "index.html not found"}

# Lista todos los cargos validados
@app.get("/cargo/list_all")
def list_all_cargos():
    result = []
    for c in CARGOS_DB:
        validated = validate_cargo(c.dict())
        result.append(validated)
    return result

# Validar y agregar un cargo nuevo
@app.post("/cargo/validate")
def validate_new_cargo(cargo: Cargo):
    if not cargo.mawb or not cargo.hawb:
        raise HTTPException(status_code=422, detail="MAWB o HAWB faltante")
    validated = validate_cargo(cargo.dict())
    CARGOS_DB.append(cargo)
    return validated
