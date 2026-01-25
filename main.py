from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="SmartCargo-AIPA")

# =========================
# MODELOS
# =========================
class CargoInput(BaseModel):
    mawb: str
    hawb: str
    origin: str
    destination: str
    cargo_type: str
    flight_date: str


class Document(BaseModel):
    doc_type: str
    status: str
    observation: str = ""
    norm: str = "IATA"


class CargoRecord(BaseModel):
    mawb: str
    semaphore: str
    documents: List[Document]


DATABASE: List[CargoRecord] = []


# =========================
# VALIDAR CARGA
# =========================
@app.post("/cargo/validate")
def validate_cargo(data: CargoInput):

    documents = [
        Document(doc_type="Air Waybill", status="Aprobado"),
        Document(doc_type="Factura Comercial", status="Observación",
                 observation="Valor declarado incompleto", norm="Aduana"),
        Document(doc_type="Lista de Empaque", status="Crítico",
                 observation="Falta firma exportador", norm="IATA / ICAO")
    ]

    semaphore = "OK"
    if any(d.status == "Crítico" for d in documents):
        semaphore = "BLOQUEADO"
    elif any(d.status == "Observación" for d in documents):
        semaphore = "REVISAR"

    cargo = CargoRecord(
        mawb=data.mawb,
        semaphore=semaphore,
        documents=documents
    )

    DATABASE.append(cargo)
    return cargo


# =========================
# LISTAR CARGAS
# =========================
@app.get("/cargo/list_all")
def list_all():
    return DATABASE
