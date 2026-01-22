from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from backend.database import SessionLocal, Cargo, Document
from backend.rules import validate_cargo
from backend.utils import cargo_summary
import shutil
import os

app = FastAPI()
STORAGE_DIR = "storage"

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
    db.close()
    return {"cargo_id": cargo.id, "message": "Cargo creado"}

@app.post("/cargo/upload")
async def upload_document(cargo_id: int = Form(...), doc_type: str = Form(...), file: UploadFile = File(...)):
    cargo_dir = os.path.join(STORAGE_DIR, str(cargo_id))
    os.makedirs(cargo_dir, exist_ok=True)
    file_path = os.path.join(cargo_dir, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    db = SessionLocal()
    doc = Document(
        cargo_id=cargo_id,
        doc_type=doc_type,
        status="pending",
        version="v1",
        responsible="user"
    )
    db.add(doc)
    db.commit()
    db.close()
    return {"message": f"{doc_type} cargado correctamente"}

@app.get("/cargo/status/{cargo_id}")
async def cargo_status(cargo_id: int):
    db = SessionLocal()
    cargo = db.query(Cargo).filter(Cargo.id==cargo_id).first()
    documents = db.query(Document).filter(Document.cargo_id==cargo_id).all()
    db.close()
    status, reasons = validate_cargo(cargo, documents)
    return {"cargo_id": cargo_id, "status": status, "reasons": reasons}
