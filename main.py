from fastapi import FastAPI, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.rules import validate_cargo
from backend.utils import cargo_dashboard, generate_advisor_message
from backend.roles import get_role_permissions
from backend.storage import save_document, list_documents, delete_document
from models import SessionLocal
from typing import List

USERNAME = "admin"
PASSWORD = "securepassword"

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")

app.mount("/static", StaticFiles(directory="static"), name="static")

def auth(username: str = Form(...), password: str = Form(...)):
    if username != USERNAME or password != PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return username

@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

@app.post("/cargo/validate")
async def cargo_validate(
    username: str = Depends(auth),
    mawb: str = Form(...),
    hawb: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...),
    weight: float = Form(...),
    volume: float = Form(...),
    length: float = Form(...),
    width: float = Form(...),
    height: float = Form(...),
):
    cargo_data = {
        "mawb": mawb,
        "hawb": hawb,
        "origin": origin,
        "destination": destination,
        "cargo_type": cargo_type,
        "flight_date": flight_date,
        "weight": weight,
        "volume": volume,
        "length": length,
        "width": width,
        "height": height
    }
    result = validate_cargo(cargo_data)
    advisor_msg = generate_advisor_message(result)
    result["advisor"] = advisor_msg
    result["legal"] = "SMARTCARGO-AIPA by May Roga LLC · Sistema de validación documental preventiva. No sustituye decisiones del operador aéreo."
    return JSONResponse(result)

@app.get("/cargo/list_all")
async def list_cargos(role: str = "owner", username: str = Depends(auth)):
    db = SessionLocal()
    cargos = cargo_dashboard(db, role)
    db.close()
    return JSONResponse(cargos)

@app.post("/cargo/upload")
async def upload_document(
    username: str = Depends(auth),
    cargo_id: int = Form(...),
    doc_type: str = Form(...),
    files: List[UploadFile] = File(...),
):
    db = SessionLocal()
    uploaded_docs = []
    for f in files:
        doc = save_document(db, f, cargo_id, doc_type, username)
        uploaded_docs.append({
            "filename": doc.filename,
            "doc_type": doc.doc_type,
            "status": doc.status
        })
    db.close()
    return JSONResponse({"uploaded": uploaded_docs})

@app.post("/cargo/delete")
async def delete_doc(
    username: str = Depends(auth),
    cargo_id: int = Form(...),
    filename: str = Form(...),
):
    db = SessionLocal()
    result = delete_document(db, cargo_id, filename, username)
    db.close()
    if result:
        return JSONResponse({"status": "deleted"})
    return JSONResponse({"status": "not_found"}, status_code=404)
