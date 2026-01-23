# main.py
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import uuid
from storage import save_document, list_documents, get_document_path, delete_document, validate_documents
from models import Cargo, Document, Base, engine, SessionLocal
from utils import generate_pdf_report
from rules import REQUIRED_DOCS

# Inicializar DB
Base.metadata.create_all(bind=engine)

# FastAPI
app = FastAPI(title="SmartCargo AIPA")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Frontend
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Crear Cargo
@app.post("/cargo/create")
async def create_cargo(
    mawb: str = Form(...),
    hawb: str = Form(""),
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
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            flight_date=datetime.strptime(flight_date, "%Y-%m-%d")
        )
        db.add(cargo)
        db.commit()
        db.refresh(cargo)
        return {"cargo_id": cargo.id, "message": "Cargo creado correctamente"}
    finally:
        db.close()

# Subir documento
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

# Listar documentos
@app.get("/cargo/list/{cargo_id}", response_class=JSONResponse)
async def list_cargo_documents(cargo_id: int):
    docs = list_documents(cargo_id)
    return {"cargo_id": cargo_id, "documents": docs}

# Obtener ruta
@app.get("/cargo/path/{cargo_id}/{filename}")
async def document_path(cargo_id: int, filename: str):
    try:
        path = get_document_path(cargo_id, filename)
        return {"cargo_id": cargo_id, "filename": filename, "path": str(path)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Eliminar documento
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

# Validar documentos y generar PDF
@app.post("/cargo/validate")
async def validate_and_pdf(cargo_id: int = Form(...)):
    validation = validate_documents(cargo_id, REQUIRED_DOCS)
    pdf_file = f"storage/advisory_{uuid.uuid4()}.pdf"
    generate_pdf_report({"cargo_id": cargo_id, **validation, "checklist": {doc: "OK" for doc in REQUIRED_DOCS}}, pdf_file)
    return {"cargo_id": cargo_id, **validation, "pdf": pdf_file}
