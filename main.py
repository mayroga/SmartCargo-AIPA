# main.py
from fastapi import FastAPI, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.database import SessionLocal
from backend.rules import validate_cargo
from backend.utils import generate_advisor_message
import json
import os

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

# Autenticación mínima
def expert_auth(username: str = Form(...), password: str = Form(...)):
    if username != "maykel" or password != os.getenv("SMARTCARGO_PASSWORD", "********"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# Página principal
@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# Validación de cargo
@app.post("/cargo/validate")
async def cargo_validate(
    mawb: str = Form(...),
    hawb: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...),
    weight_kg: float = Form(...),
    length_cm: float = Form(...),
    width_cm: float = Form(...),
    height_cm: float = Form(...),
    role: str = Form(...),
    documents_json: str = Form("[]"),
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    try:
        documents = json.loads(documents_json)
    except:
        documents = []

    cargo_data = {
        "mawb": mawb,
        "hawb": hawb,
        "origin": origin,
        "destination": destination,
        "cargo_type": cargo_type,
        "flight_date": flight_date,
        "weight_kg": weight_kg,
        "length_cm": length_cm,
        "width_cm": width_cm,
        "height_cm": height_cm,
        "role": role,
        "documents": documents
    }

    # Validar reglas
    validation_result = validate_cargo(cargo_data)

    # Asesor IA
    advisor_msg = await generate_advisor_message(cargo_data, validation_result)

    return JSONResponse({
        "semaforo": validation_result.get("semaforo", "🔴"),
        "documents_required": validation_result.get("required_docs", []),
        "missing_docs": validation_result.get("missing_docs", []),
        "overweight": validation_result.get("overweight", False),
        "oversized": validation_result.get("oversized", False),
        "explanation": validation_result.get("explanation", ""),
        "advisor": advisor_msg
    })

# Subida de documentos
@app.post("/cargo/upload_document")
async def upload_document(
    doc_type: str = Form(...),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    upload_dir = Path("storage/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return JSONResponse({
        "filename": file.filename,
        "description": doc_type,
        "uploaded_by": uploaded_by,
        "url": f"/static/uploads/{file.filename}"
    })

# Listado temporal de documentos
@app.get("/cargo/list_documents")
async def list_docs(db=Depends(get_db), auth=Depends(expert_auth)):
    upload_dir = Path("storage/uploads")
    files = []
    if upload_dir.exists():
        for f in upload_dir.iterdir():
            files.append({"filename": f.name, "url": f"/static/uploads/{f.name}"})
    return JSONResponse(files)
