# main.py

from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

from models import Cargo, Document, Base, engine, SessionLocal
from storage import save_document, list_documents, get_document_path, delete_document, validate_documents
from utils import admin_auth

load_dotenv()

# -------------------
# Base de datos
# -------------------
Base.metadata.create_all(bind=engine)

# -------------------
# App FastAPI
# -------------------
app = FastAPI(title="SmartCargo AIPA")
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------
# Home Page
# -------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
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
            flight_date=flight_date
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
        return {"message": f"Documento '{doc_type}' cargado correctamente", "filename": doc.filename, "version": doc.version}
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
# Obtener ruta de documento
# -------------------
@app.get("/cargo/path/{cargo_id}/{filename}")
async def document_path(cargo_id: int, filename: str):
    try:
        path = get_document_path(cargo_id, filename)
        return {"cargo_id": cargo_id, "filename": filename, "path": path}
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
# Validar documentos obligatorios
# -------------------
@app.post("/cargo/validate")
async def validate_cargo_documents(cargo_id: int = Form(...), required_docs: List[str] = Form(...)):
    db: Session = SessionLocal()
    try:
        result = validate_documents(db, cargo_id, required_docs)
        return {"cargo_id": cargo_id, "validation": result}
    finally:
        db.close()

# -------------------
# Panel privado admin con IA SmartCargo-AIPA
# -------------------
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(username: str = Form(...), password: str = Form(...)):
    if not admin_auth(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    with open("frontend/admin.html", "r", encoding="utf-8") as f:
        return f.read()
