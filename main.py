from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.database import SessionLocal
from backend.roles import verify_user, UserRole
from backend.rules import validate_cargo_rules
from backend.storage import save_document, list_documents
from backend.utils import cargo_dashboard, generate_advisor_message

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC · Sistema de validación documental preventiva")

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
    if username != "maykel" or password != "********":  # reemplazar con clave real segura
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
    weight_lbs: float = Form(...),
    length_cm: float = Form(...),
    width_cm: float = Form(...),
    height_cm: float = Form(...),
    role: str = Form(...),
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    cargo_data = {
        "mawb": mawb,
        "hawb": hawb,
        "origin": origin,
        "destination": destination,
        "cargo_type": cargo_type,
        "flight_date": flight_date,
        "weight_kg": weight_kg,
        "weight_lbs": weight_lbs,
        "length_cm": length_cm,
        "width_cm": width_cm,
        "height_cm": height_cm,
        "role": role
    }
    # Validar reglas duras Avianca/IATA/DG
    validation_status = validate_cargo_rules(cargo_data)
    # Obtener semáforo y asesor educativo
    dashboard = cargo_dashboard(cargo_data, validation_status)
    advisor_msg = generate_advisor_message(cargo_data, validation_status)

    return JSONResponse({
        "status": dashboard["semaforo"],
        "documents_required": dashboard["documents_required"],
        "advisor": advisor_msg
    })

# -----------------------------
# Endpoint para subir documentos
# -----------------------------
@app.post("/cargo/upload_document")
async def upload_document(
    cargo_id: int = Form(...),
    doc_type: str = Form(...),
    uploaded_by: str = Form(...),
    file: bytes = Form(...),
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    doc = save_document(db, file, cargo_id, doc_type, uploaded_by)
    return JSONResponse({"message": "Documento cargado correctamente", "document": doc.filename})

# -----------------------------
# Endpoint lista de documentos
# -----------------------------
@app.get("/cargo/list_documents/{cargo_id}")
async def list_docs(cargo_id: int, db=Depends(get_db), auth=Depends(expert_auth)):
    docs = list_documents(cargo_id)
    return JSONResponse(docs)
