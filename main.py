import uvicorn
from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import Usuario, Carga, Documento, ResultadoValidacion
from rules import validar_carga
from storage import save_document, list_documents
from roles import view_for_role, can
from ai_helper import ai_document_checker
from config import BASE_DIR, OPENAI_API_KEY

# ----------------------------
# APP FASTAPI
# ----------------------------
app = FastAPI(title="SMARTCARGO-AIPA by MAY ROGA LLC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# DEPENDENCIAS SIMPLES
# ----------------------------
def get_usuario(role: str = Form(...)):
    return Usuario(role=role)

# ----------------------------
# ENDPOINT: CREAR CARGA
# ----------------------------
@app.post("/create_cargo")
async def create_cargo(
    mawb: str = Form(...),
    hawb: str = Form(""),
    airline: str = Form("Avianca Cargo"),
    origin: str = Form(...),
    destination: str = Form(...),
    flight_date: str = Form(...),
    cargo_type: str = Form(...),
):
    # Validación mínima de identidad
    if cargo_type not in ["GEN", "DG", "PER", "HUM", "AVI", "VAL"]:
        raise HTTPException(status_code=400, detail="Tipo de carga inválido")
    cargo = Carga(
        mawb=mawb,
        hawb=hawb,
        airline=airline,
        origin=origin,
        destination=destination,
        flight_date=flight_date,
        cargo_type=cargo_type
    )
    return {"cargo_id": cargo.id, "message": "Carga creada exitosamente"}

# ----------------------------
# ENDPOINT: SUBIR DOCUMENTOS
# ----------------------------
@app.post("/upload_docs/{cargo_id}")
async def upload_docs(
    cargo_id: str,
    files: List[UploadFile],
    uploaded_by: str = Form(...)
):
    saved_docs = []
    for file in files:
        doc_name = file.filename.split('.')[0]
        doc = save_document(file, cargo_id, doc_name, uploaded_by)
        saved_docs.append(doc)
    return {"message": f"{len(saved_docs)} documentos guardados", "documents": [d.name for d in saved_docs]}

# ----------------------------
# ENDPOINT: VALIDACIÓN Y RESULTADO OPERATIVO
# ----------------------------
@app.get("/validate_cargo/{cargo_id}")
async def validate_cargo(cargo_id: str, user: Usuario = Depends(get_usuario)):

    # 1️⃣ Listar documentos cargados
    doc_files = list_documents(cargo_id)
    if not doc_files:
        return JSONResponse(content={"status": "🔴 NO ACEPTABLE", "reason": "No hay documentos cargados"}, status_code=200)

    # 2️⃣ Crear objetos Documento con trazabilidad dummy (para ejemplo)
    documentos = [Documento(name=f, status="✔ Válido", version="1", uploaded_by="user", upload_date=None) for f in doc_files]

    # 3️⃣ IA auxiliar: detectar inconsistencias y formatos
    documentos = ai_document_checker(documentos)

    # 4️⃣ Motor de reglas Avianca-first
    resultado = validar_carga(cargo_id, documentos)

    # 5️⃣ Ajuste por rol
    vista = view_for_role(user, resultado)
    return {"cargo_id": cargo_id, "role": user.role, "operational_result": vista}

# ----------------------------
# ENDPOINT: TEST SEMÁFORO
# ----------------------------
@app.get("/semaforo_demo")
async def semaforo_demo():
    return {
        "example_status": "🟢 LISTA PARA ACEPTACIÓN",
        "example_reason": [
            "Invoice con Incoterm correcto",
            "Packing List coincide con piezas",
            "MSDS vigente",
            "Copias dentro y fuera del folder"
        ]
    }

# ----------------------------
# RUN LOCAL
# ----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
