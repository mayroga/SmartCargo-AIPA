from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.rules import validate_cargo
from backend.utils import cargo_dashboard, generate_advisor_message
from backend.roles import verify_user

app = FastAPI(
    title="SMARTCARGO-AIPA by May Roga LLC · Preventive Documentary Validation System"
)

# Montar carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------------
# Autenticación mínima experto
# -----------------------------
def expert_auth(username: str = Form(...), password: str = Form(...)):
    if username != "maykel" or password != "********":
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
    role: str = Form(...),
    documents: str = Form(None),  # JSON string con docs y descripciones
    auth=Depends(expert_auth)
):
    import json
    try:
        docs = json.loads(documents) if documents else []
    except:
        docs = []

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
        "documents": docs
    }

    validation = validate_cargo(cargo_data)
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
