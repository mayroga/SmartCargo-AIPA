from fastapi import FastAPI, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.database import SessionLocal
from backend.roles import verify_user, UserRole
from backend.rules import validate_cargo
from backend.utils import cargo_dashboard, generate_advisor_message
from backend.storage import save_document, list_documents

app = FastAPI(
    title="SMARTCARGO-AIPA by May Roga LLC · Sistema de validación documental preventiva"
)

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
# Servir frontend
# -----------------------------
@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# -----------------------------
# Validación de Cargo
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
    role: str = Form(...),
    documents: list = Form([]),  # lista de nombres de archivos subidos
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
        "length_cm": length_cm,
        "width_cm": width_cm,
        "height_cm": height_cm,
        "role": role,
        "documents": [{"filename": d} for d in documents]
    }

    # Validación de reglas duras Avianca/IATA/TSA/CBP
    validation = validate_cargo(cargo_data)

    # Generar dashboard y asesor
    dashboard = cargo_dashboard(cargo_data, validation)
    advisor_msg = generate_advisor_message(cargo_data, validation)

    return JSONResponse({
        "semaforo": dashboard["semaforo"],
        "documents_required": dashboard["documents_required"],
        "missing_docs": dashboard["missing_docs"],
        "overweight": dashboard["overweight"],
        "oversized": dashboard["oversized"],
        "advisor": advisor_msg
    })

# -----------------------------
# Subida de documentos (temporal, solo evidencia)
# -----------------------------
@app.post("/cargo/upload_document")
async def upload_document(
    cargo_id: int = Form(...),
    doc_type: str = Form(...),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    db=Depends(get_db),
    auth=Depends(expert_auth)
):
    doc = save_document(db, file, cargo_id, doc_type, uploaded_by)
    return JSONResponse({"message": "Documento cargado correctamente", "document": doc.filename})

# -----------------------------
# Listar documentos
# -----------------------------
@app.get("/cargo/list_documents/{cargo_id}")
async def list_docs(cargo_id: int, db=Depends(get_db), auth=Depends(expert_auth)):
    docs = list_documents(cargo_id)
    return JSONResponse(docs)

# -----------------------------
# Endpoint dinámico según rol (puede expandirse)
# -----------------------------
@app.get("/role/view/{role_name}")
async def view_by_role(role_name: str, auth=Depends(expert_auth)):
    allowed_roles = [UserRole.SHIPPER, UserRole.FORWARDER, UserRole.CHOFER,
                     UserRole.WAREHOUSE, UserRole.OPERADOR, UserRole.DESTINATARIO]
    verify_user(role_name, allowed_roles)

    # Aquí se podría retornar la vista adaptada según rol
    return JSONResponse({
        "message": f"View loaded for role: {role_name}",
        "role": role_name,
        "instructions": f"Fields editable and documents visible only for {role_name}."
    })
