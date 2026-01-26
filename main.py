from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.database import SessionLocal
from backend.roles import verify_user
from backend.rules import validate_cargo
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
    if username != "maykel" or password != "********":  # reemplazar con clave real
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
async def cargo_validate(request: Request, db=Depends(get_db), auth=Depends(expert_auth)):
    data = await request.json()
    cargo_data = {
        "mawb": data.get("mawb"),
        "hawb": data.get("hawb"),
        "origin": data.get("origin"),
        "destination": data.get("destination"),
        "cargo_type": data.get("cargo_type"),
        "flight_date": data.get("flight_date"),
        "weight_kg": data.get("weight_kg"),
        "length_cm": data.get("length_cm"),
        "width_cm": data.get("width_cm"),
        "height_cm": data.get("height_cm"),
        "role": data.get("role"),
        "documents": data.get("documents", [])
    }

    # Validación estricta
    validation = validate_cargo(cargo_data)
    dashboard = cargo_dashboard(cargo_data, validation)
    advisor_msg = generate_advisor_message(cargo_data, validation)

    return JSONResponse({
        "semaforo": dashboard["semaforo"],
        "documents_required": dashboard["documents_required"],
        "missing_docs": dashboard.get("missing_docs", []),
        "overweight": dashboard.get("overweight", False),
        "oversized": dashboard.get("oversized", False),
        "advisor": advisor_msg
    })
