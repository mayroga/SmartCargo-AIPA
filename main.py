# main.py
from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="SmartCargo AIPA Backend")

# CORS para front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------------------
# Simulación de base temporal
# -------------------------------
# Cada cargo es un dict con documentos
cargo_db = [
    {
        "id": 1,
        "mawb": "123-4567890",
        "hawb": "HAWB001",
        "origin": "MIA",
        "destination": "BOG",
        "cargo_type": "General",
        "flight_date": "2026-01-25",
        "documents": [
            {"doc_type": "Invoice", "filename": "invoice1.pdf", "version": "1.0", "upload_date": "2026-01-20", "valid_until": None},
            {"doc_type": "Packing List", "filename": "packing1.pdf", "version": "1.0", "upload_date": "2026-01-20", "valid_until": None},
            {"doc_type": "SLI", "filename": "sli1.pdf", "version": "1.0", "upload_date": "2026-01-20", "valid_until": None},
            {"doc_type": "MSDS", "filename": "msds1.pdf", "version": "1.0", "upload_date": "2025-12-01", "valid_until": "2026-01-01"},  # Vencido
        ]
    }
]

# -------------------------------
# Login admin simple
# -------------------------------
def admin_auth(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "1234":
        return True
    raise HTTPException(status_code=401, detail="Unauthorized")

# -------------------------------
# Listar todos los cargos
# -------------------------------
@app.get("/cargo/list_all")
async def list_all():
    return cargo_db

# -------------------------------
# Listar documentos de cargo
# -------------------------------
@app.get("/cargo/list/{cargo_id}")
async def list_documents(cargo_id: int):
    cargo = next((c for c in cargo_db if c["id"] == cargo_id), None)
    if not cargo:
        return {"documents": []}
    return {"documents": cargo["documents"]}

# -------------------------------
# Validate Cargo según checklist Avianca
# -------------------------------
@app.post("/cargo/validate")
async def validate_cargo(
    mawb: str = Form(...),
    hawb: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...)
):
    # Buscar cargo
    cargo = next((c for c in cargo_db if c["mawb"] == mawb), None)
    if not cargo:
        return JSONResponse({"message": "Cargo not found", "status": "🔴 NO ACEPTABLE", "reasons": ["Cargo no existe en el sistema."]})

    documents = cargo.get("documents", [])
    reasons = []

    # Checklist Avianca
    doc_types_required = ["Invoice", "Packing List", "SLI", "MSDS"]
    semaforo = "🟢 LISTO PARA COUNTER"

    today = datetime.today().date()

    for doc_type in doc_types_required:
        doc = next((d for d in documents if d["doc_type"] == doc_type), None)
        if not doc:
            semaforo = "🔴 NO ACEPTABLE"
            reasons.append(f"{doc_type} faltante.")
        else:
            # MSDS vencido
            if doc_type == "MSDS" and doc.get("valid_until"):
                valid_until = datetime.strptime(doc["valid_until"], "%Y-%m-%d").date()
                if valid_until < today:
                    semaforo = "🔴 NO ACEPTABLE"
                    reasons.append("MSDS vencido.")

            # Packing List inconsistente (simulado)
            if doc_type == "Packing List" and "incorrecto" in doc.get("filename","").lower():
                semaforo = "🟡 ACEPTABLE CON RIESGO"
                reasons.append("Packing List inconsistente.")

            # Invoice incompleto (simulado)
            if doc_type == "Invoice" and "incomplete" in doc.get("filename","").lower():
                semaforo = "🟡 ACEPTABLE CON RIESGO"
                reasons.append("Invoice incompleto.")

    if not reasons:
        reasons.append("Todos los documentos correctos según checklist Avianca.")

    # Nota legal
    legal_note = "SmartCargo-AIPA es asesor, no autoridad. Aceptación final depende de Avianca, IATA, CBP, TSA y DOT."

    return JSONResponse({
        "message": f"Cargo evaluado: {semaforo}",
        "status": semaforo,
        "reasons": reasons,
        "legal_note": legal_note
    })
