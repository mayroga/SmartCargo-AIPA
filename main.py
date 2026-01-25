from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.rules import validate_cargo
from backend.storage import save_document, list_documents, delete_document
from backend.utils import cargo_dashboard, generate_advisor_message
from backend.database import SessionLocal

app = FastAPI(title="SmartCargo-AIPA · Asesor documental preventivo")

# Monta la carpeta 'static' (JS/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------------
# Ruta principal -> frontend
# -----------------------------
@app.get("/")
async def serve_index():
    index_path = Path("frontend/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# -----------------------------
# Endpoints de cargo
# -----------------------------
@app.post("/cargo/validate")
async def cargo_validate(
    mawb: str = Form(...),
    hawb: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...),
    weight: float = Form(...),
    volume: float = Form(...),
    role: str = Form(...),  # Shipper, Forwarder, Driver, Warehouse
    file1: UploadFile = File(None),
    file2: UploadFile = File(None)
):
    db = SessionLocal()
    cargo_data = {
        "mawb": mawb,
        "hawb": hawb,
        "origin": origin,
        "destination": destination,
        "cargo_type": cargo_type,
        "flight_date": flight_date,
        "weight": weight,
        "volume": volume,
        "role": role
    }

    # Guardar documentos si se suben
    uploaded_files = []
    if file1:
        doc1 = save_document(db, file1, mawb, "Documento 1", role)
        uploaded_files.append(doc1.filename)
    if file2:
        doc2 = save_document(db, file2, mawb, "Documento 2", role)
        uploaded_files.append(doc2.filename)

    # Validación de cargo y documentos
    try:
        cargo_status = validate_cargo(cargo_data)
        dashboard = cargo_dashboard(cargo_data)
        advisor = generate_advisor_message(cargo_data, cargo_status)

        response = {
            "cargo_status": cargo_status,
            "dashboard": dashboard,
            "advisor_message": advisor,
            "uploaded_files": uploaded_files,
            "system": "SMARTCARGO-AIPA by May Roga LLC · Sistema de validación documental preventiva."
        }
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# -----------------------------
# Listar documentos por cargo
# -----------------------------
@app.get("/cargo/{mawb}/documents")
async def cargo_documents(mawb: str):
    db = SessionLocal()
    docs = list_documents(mawb)
    return JSONResponse(docs)

# -----------------------------
# Borrar documento
# -----------------------------
@app.delete("/cargo/{mawb}/document/{filename}")
async def delete_cargo_document(mawb: str, filename: str, deleted_by: str = Form(...)):
    db = SessionLocal()
    result = delete_document(db, mawb, filename, deleted_by)
    return JSONResponse({"deleted": result})
