# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict
from backend.database import SessionLocal
from backend.roles import verify_user, UserRole
from backend.rules import validate_cargo
from backend.utils import generate_advisor_message
import os
import json

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC · Preventive Documentary Validation System")

# Montar carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base de datos temporal
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Autenticación mínima experto
# -----------------------------
def expert_auth(username: str, password: str):
    if username != "maykel" or password != os.getenv("SMARTCARGO_PASSWORD", "********"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# -----------------------------
# Modelos Pydantic
# -----------------------------
class DocumentModel(BaseModel):
    filename: str
    description: str

class CargoModel(BaseModel):
    mawb: str
    hawb: str
    origin: str
    destination: str
    cargo_type: str
    flight_date: str
    weight_kg: float
    length_cm: float
    width_cm: float
    height_cm: float
    volume_m3: float
    role: str
    aircraft_type: str = "A320Family"
    documents: List[DocumentModel] = []

# -----------------------------
# Ruta principal
# -----------------------------
@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# -----------------------------
# Endpoint Validación de Cargo
# -----------------------------
@app.post("/cargo/validate")
async def cargo_validate(cargo: CargoModel, db=Depends(get_db), auth=Depends(expert_auth)):
    cargo_data = cargo.dict()

    # Validar reglas duras Avianca/IATA/TSA/CBP/DG/Perishable
    validation_result = validate_cargo(cargo_data)

    # Generar asesoramiento operativo/legal
    advisor_msg = await generate_advisor_message(cargo_data, validation_result)

    # Resultado completo con semáforo legal y explicaciones
    return JSONResponse({
        "semaforo": validation_result["semaforo"],
        "documents_required": validation_result["required_docs"],
        "missing_docs": validation_result["missing_docs"],
        "overweight": validation_result["overweight"],
        "oversized": validation_result["oversized"],
        "explanation": validation_result.get("explanation", ""),
        "advisor": advisor_msg
    })

# -----------------------------
# Endpoint para subir documentos temporalmente
# -----------------------------
@app.post("/cargo/upload_document")
async def upload_document(
    cargo_id: int,
    doc_type: str,
    uploaded_by: str,
    file: bytes,
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    upload_dir = Path("storage/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{uploaded_by}_{doc_type}_{Path(file.name).name}"
    with open(file_path, "wb") as f:
        f.write(file)

    return JSONResponse({
        "filename": Path(file_path).name,
        "description": doc_type,
        "uploaded_by": uploaded_by,
        "url": f"/static/uploads/{Path(file_path).name}"
    })

# -----------------------------
# Endpoint lista de documentos
# -----------------------------
@app.get("/cargo/list_documents/{cargo_id}")
async def list_docs(cargo_id: int, db=Depends(get_db), auth=Depends(expert_auth)):
    upload_dir = Path("storage/uploads")
    files = []
    if upload_dir.exists():
        for f in upload_dir.iterdir():
            files.append({
                "filename": f.name,
                "url": f"/static/uploads/{f.name}"
            })
    return JSONResponse(files)
