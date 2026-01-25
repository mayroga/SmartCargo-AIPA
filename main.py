# main.py
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from storage import save_document, list_documents, get_document_path, delete_document
from models import Cargo, Document, Base, engine, SessionLocal

# -------------------
# Inicialización DB
# -------------------
Base.metadata.create_all(bind=engine)

# -------------------
# FastAPI App
# -------------------
app = FastAPI(title="SmartCargo AIPA")
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------
# Página principal
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
                    "audit_notes": doc.audit_notes
                })
            result.append(cargo_dict)
        return result
    finally:
        db.close()

# -------------------
# Validar cargo según checklist Avianca
# -------------------
@app.post("/cargo/validate")
async def validate_cargo_documents(cargo_id: int = Form(...)):
    db: Session = SessionLocal()
    try:
        cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo no encontrado")

        documents = {doc.doc_type: doc for doc in cargo.documents}
        reasons = []

        # Reglas Avianca
        required_docs = ["Commercial Invoice", "Packing List", "SLI", "MSDS"]
        for doc_name in required_docs:
            if doc_name not in documents:
                reasons.append(f"Falta {doc_name}")

        # Packing List vs Invoice
        if "Commercial Invoice" in documents and "Packing List" in documents:
            inv = documents["Commercial Invoice"]
            pack = documents["Packing List"]
            if inv.filename != pack.filename:
                reasons.append("Packing List no coincide con Invoice")

        # MSDS vigente
        if "MSDS" in documents and documents["MSDS"].expiration_date:
            if documents["MSDS"].expiration_date < datetime.today():
                reasons.append("MSDS vencido")

        # Determinar semáforo
        if reasons:
            status = "🔴 NO ACEPTABLE"
        else:
            status = "🟢 LISTO PARA COUNTER"

        # Nota legal
        reasons.append("SmartCargo-AIPA es asesor, no autoridad. La aceptación final depende de Avianca, IATA, CBP, TSA y DOT.")

        return {"cargo_id": cargo.id, "status": status, "reasons": reasons}
    finally:
        db.close()
