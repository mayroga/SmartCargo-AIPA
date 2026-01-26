# main.py
from fastapi import FastAPI, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.database import SessionLocal
from backend.roles import verify_user, UserRole
from backend.rules import validate_cargo
from backend.utils import generate_advisor_message
import os
import json

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC · Preventive Documentary Validation System")

# Carpeta estática
app.mount("/static", StaticFiles(directory="static"), name="static")

# DB temporal
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth experto
def expert_auth(username: str = Form(...), password: str = Form(...)):
    if username != "maykel" or password != os.getenv("SMARTCARGO_PASSWORD", "********"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# Ruta principal
@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# Validación de carga
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
    documents_json: str = Form(...),
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    # Parse JSON documentos
    try:
        documents = json.loads(documents_json)
    except Exception:
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

    # Validación reglas Avianca/IATA/TSA/CBP/DG/Perishable
    validation_result = validate_cargo(cargo_data)

    # Mensaje asesor IA
    advisor_msg = await generate_advisor_message(cargo_data, validation_result)

    return JSONResponse({
        "semaforo": validation_result["semaforo"],
        "documents_required": validation_result["required_docs"],
        "missing_docs": validation_result["missing_docs"],
        "overweight": validation_result["overweight"],
        "oversized": validation_result["oversized"],
        "explanation": validation_result["explanation"],
        "advisor": advisor_msg
    })

# Subir documentos
@app.post("/cargo/upload_document")
async def upload_document(
    cargo_id: int = Form(...),
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

# Listar documentos
@app.get("/cargo/list_documents/{cargo_id}")
async def list_docs(cargo_id: int, db=Depends(get_db), auth=Depends(expert_auth)):
    upload_dir = Path("storage/uploads")
    files = []
    if upload_dir.exists():
        for f in upload_dir.iterdir():
            files.append({"filename": f.name, "url": f"/static/uploads/{f.name}"})
    return JSONResponse(files)
