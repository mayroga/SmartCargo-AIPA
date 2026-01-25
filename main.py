# main.py – SmartCargo-AIPA Backend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from rules import validate_cargo

app = FastAPI(title="Asesor SmartCargo-AIPA")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/cargo/list_all")
def list_all_cargos():
    """
    Retorna todos los cargos con semáforo y estado de documentos
    """
    result = []
    for c in CARGOS_DB:
        validated = validate_cargo(c.dict())
        result.append(validated)
    return result

@app.post("/cargo/validate")
def validate_new_cargo(cargo: Cargo):
    """
    Valida un nuevo cargo y lo agrega a la DB simulada
    """
    if not cargo.mawb or not cargo.hawb:
        raise HTTPException(status_code=422, detail="MAWB o HAWB faltante")

    validated = validate_cargo(cargo.dict())
    CARGOS_DB.append(cargo)
    return validated

@app.get("/")
def root():
    return {"message": "Asesor SmartCargo-AIPA Backend operativo"}
