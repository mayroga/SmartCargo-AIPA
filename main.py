# main.py
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

# Importar módulos locales
from storage import save_document, list_documents, get_document_path, delete_document
from backend.rules import validate_cargo_documents as validate_cargo
from models import Cargo, Document, Base, engine, SessionLocal

# -------------------
# Inicialización DB
# -------------------
Base.metadata.create_all(bind=engine)

# -------------------
# FastAPI App
# -------------------
app = FastAPI(title="SmartCargo AIPA")

# -------------------
# Montar archivos estáticos
# -------------------
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------
# Página principal
# -------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = os.path.join("frontend", "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<h1>Index.html no encontrado</h1>", status_code=404)
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

# -------------------
# Crear Cargo
# -------------------
@app.post("/cargo/create")
async def create_cargo(
    mawb: str = Form(...),
    hawb: str = Form(""),
    airline: str = Form("Avianca Cargo"),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    flight_date: str = Form(...)
):
    db: Session = SessionLocal()
    try:
        cargo = Cargo(
            mawb=mawb,
            hawb=hawb,
            airline=airline,
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            weight=weight,
            flight_date=datetime.strptime(flight_date, "%Y-%m-%d")
        )
        db.add(cargo)
        db.commit()
        db.refresh(cargo)
        return {"cargo_id": cargo.id, "message": "Cargo creado correctamente"}
    finally:
        db.close()

# -------------------
# Subir documento
# -------------------
@app.post("/cargo/upload")
async def upload_document(
    cargo_id: int = Form(...),
    doc_type: str = Form(...),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...)
):
    db: Session = SessionLocal()
    try:
        doc = save_document(db=db, file=file, cargo_id=cargo_id, doc_type=doc_type, uploaded_by=uploaded_by)
        return {
            "message": f"Documento '{doc_type}' cargado correctamente",
            "filename": doc.filename,
            "version": doc.version
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# -------------------
# Listar documentos de un cargo
# -------------------
@app.get("/cargo/list/{cargo_id}", response_class=JSONResponse)
async def list_cargo_documents(cargo_id: int):
    docs = list_documents(cargo_id)
    return {"cargo_id": cargo_id, "documents": docs}

# -------------------
# Listar todos los cargos
# -------------------
@app.get("/cargo/list_all", response_class=JSONResponse)
async def list_all_cargos():
    db: Session = SessionLocal()
    try:
        cargos = db.query(Cargo).all()
        result = []
        for cargo in cargos:
            cargo_dict = {
                "id": cargo.id,
                "mawb": cargo.mawb,
                "hawb": cargo.hawb,
                "airline": cargo.airline,
                "origin": cargo.origin,
                "destination": cargo.destination,
                "cargo_type": cargo.cargo_type,
                "weight": cargo.weight,
                "flight_date": cargo.flight_date.strftime("%Y-%m-%d"),
                "documents": []
            }
            for doc in cargo.documents:
                cargo_dict["documents"].append({
                    "doc_type": doc.doc_type,
                    "filename": doc.filename,
                    "version": doc.version,
                    "status": doc.status,
                    "responsible": doc.responsible,
                    "upload_date": doc.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "audit_notes": doc.audit_notes,
                    "weight": doc.weight if hasattr(doc, "weight") else cargo.weight
                })
            result.append(cargo_dict)
        return result
    finally:
        db.close()

# -------------------
# Obtener ruta de documento
# -------------------
@app.get("/cargo/path/{cargo_id}/{filename}")
async def document_path(cargo_id: int, filename: str):
    try:
        path = get_document_path(cargo_id, filename)
        return {"cargo_id": cargo_id, "filename": filename, "path": str(path)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# -------------------
# Eliminar documento
# -------------------
@app.delete("/cargo/delete/{cargo_id}/{filename}")
async def remove_document(cargo_id: int, filename: str, deleted_by: str = Form(...)):
    db: Session = SessionLocal()
    try:
        success = delete_document(db=db, cargo_id=cargo_id, filename=filename, deleted_by=deleted_by)
        if not success:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return {"cargo_id": cargo_id, "filename": filename, "status": "deleted"}
    finally:
        db.close()

# -------------------
# Validar cargo tipo SmartCargo-AIPA (para Avianca/IATA/CBP)
# -------------------
@app.post("/cargo/validate")
async def validate_cargo_endpoint(
    cargo_id: int = Form(...),
    user: str = Form(...),
):
    """
    Evalúa todos los documentos de un cargo según reglas Avianca/IATA/CBP/TSA/DOT.
    Devuelve semáforo operativo 🔴/🟡/🟢, peso, documentos faltantes y motivos claros.
    """
    db: Session = SessionLocal()
    try:
        cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo no encontrado")

        # Ejecutar validación profesional SmartCargo-AIPA
        semaforo, motivos = validate_cargo(cargo)

        # Evaluar peso y alerta de aceptación
        peso = cargo.weight
        if peso > 1000:  # Ejemplo: límite de Avianca
            motivos.append("Peso excede límite de aceptación Avianca")

        # Formato de respuesta completo
        return {
            "cargo_id": cargo.id,
            "status": semaforo,
            "weight": peso,
            "motivos": motivos,
            "legal": "SmartCargo-AIPA es asesor; aceptación final depende de Avianca/IATA/CBP/TSA/DOT."
        }
    finally:
        db.close()
