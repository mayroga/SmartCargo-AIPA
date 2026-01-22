# main.py

from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from backend.database import SessionLocal, Cargo, Document
from backend.utils import cargo_summary
from backend.storage import save_document, list_documents
import os

app = FastAPI()

# ----------------------------
# ENDPOINTS FRONTEND
# ----------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

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
    db = SessionLocal()
    cargo = Cargo(
        mawb=mawb, hawb=hawb, airline=airline,
        origin=origin, destination=destination,
        cargo_type=cargo_type, flight_date=flight_date
    )
    db.add(cargo)
    db.commit()
    db.refresh(cargo)
    db.close()
    return {"cargo_id": cargo.id, "message": "Cargo creado"}

@app.post("/cargo/upload")
async def upload_document(
    cargo_id: int = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    role: str = Form(...)
):
    if role not in ["admin", "user", "auditor"]:
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    meta = save_document(file, str(cargo_id), doc_type, uploaded_by=role)

    # Guardar registro en DB
    db = SessionLocal()
    doc = Document(
        cargo_id=cargo_id,
        doc_type=doc_type,
        version=str(meta["version"]),
        status="pending",
        responsible=role
    )
    db.add(doc)
    db.commit()
    db.close()

    return {"message": f"{doc_type} cargado correctamente", "meta": meta}

@app.get("/cargo/status/{cargo_id}/{role}")
async def cargo_status(cargo_id: int, role: str):
    db = SessionLocal()
    cargo = db.query(Cargo).filter(Cargo.id==cargo_id).first()
    documents = db.query(Document).filter(Document.cargo_id==cargo_id).all()
    db.close()
    summary = cargo_summary(cargo, documents, role)
    return JSONResponse(content=summary)

@app.get("/cargo/list_files/{cargo_id}/{role}")
async def list_files(cargo_id: int, role: str):
    """
    Endpoint para listar archivos físicos en storage
    """
    try:
        docs = list_documents(str(cargo_id), role)
        return {"cargo_id": cargo_id, "role": role, "files": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
