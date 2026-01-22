# main.py

from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List
import os

from storage import save_document, list_documents, get_document_path, delete_document, validate_documents
from models import Cargo, Document, Base, SessionLocal, engine

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
# Seguridad Admin
# -------------------
security = HTTPBasic()

def get_admin_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if credentials.username == username and credentials.password == password:
        return True
    raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

# -------------------
# Endpoints Frontend
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
# Listar documentos físicos de un cargo
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
        return {"cargo_id": cargo_id, "filename": filename, "path": str(path)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# -------------------
# Eliminar documento (auditoría y roles)
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
    result = validate_documents(cargo_id, required_docs)
    return result

# -------------------
# Auditoría Admin
# -------------------
@app.get("/admin/audit/{cargo_id}")
def audit_cargo(cargo_id: int, admin: bool = Depends(get_admin_user)):
    db = SessionLocal()
    try:
        cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo no encontrado")
        return {
            "cargo": {
                "id": cargo.id,
                "mawb": cargo.mawb,
                "hawb": cargo.hawb,
                "origin": cargo.origin,
                "destination": cargo.destination,
                "cargo_type": cargo.cargo_type,
                "flight_date": cargo.flight_date.isoformat(),
                "documents": [
                    {
                        "doc_type": doc.doc_type,
                        "filename": doc.filename,
                        "version": doc.version,
                        "status": doc.status,
                        "responsible": doc.responsible,
                        "upload_date": doc.upload_date.isoformat(),
                        "audit_notes": doc.audit_notes,
                    } for doc in cargo.documents
                ]
            }
        }
    finally:
        db.close()
