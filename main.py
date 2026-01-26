from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Dict
from backend.database import SessionLocal
from backend.roles import verify_user, UserRole
from backend.rules import validate_cargo
from backend.utils import generate_advisor_message
import json

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC · Preventive Documentary Validation System")

# Montar carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Autenticación mínima para experto SMARTCARGO-AIPA
# -----------------------------
def expert_auth(username: str = Form(...), password: str = Form(...)):
    if username != "maykel" or password != "********":  # reemplazar con clave segura real
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# -----------------------------
# Ruta principal
# -----------------------------
@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# -----------------------------
# Endpoint Validación de Cargo
# -----------------------------
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
    volume_m3: float = Form(...),
    role: str = Form(...),
    documents: str = Form(...),  # JSON string: [{"filename": "...", "description": "..."}]
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    try:
        docs_list = json.loads(documents)
    except Exception:
        docs_list = []

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
        "volume_m3": volume_m3,
        "role": role,
        "documents": docs_list
    }

    # Validación estricta y cálculo de semáforo
    validation_results = validate_cargo(cargo_data)

    # Mensaje de asesor legal y operativo usando IA o lógica interna
    advisor_msg = generate_advisor_message(cargo_data, validation_results)

    # Preparar respuesta
    response = {
        "semaforo": validation_results["semaforo"],
        "documents_required": validation_results["required_docs"],
        "missing_docs": validation_results["missing_docs"],
        "overweight": validation_results["overweight"],
        "oversized": validation_results["oversized"],
        "explanation": validation_results["explanation"],  # explicación legal detallada
        "advisor": advisor_msg
    }

    return JSONResponse(response)
