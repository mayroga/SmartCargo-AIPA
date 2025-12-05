from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import os, uuid, shutil, datetime

app = FastAPI(title="SmartCargo-AIPA Backend")

# ================== CORS ==================
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================== DATA ==================
cargas_db = []  # lista de cargas
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)

# ================== ROUTES ==================
@app.get("/")
async def root():
    return {
        "message":"SmartCargo-AIPA Backend activo",
        "mode":"free",
        "routes":["/cargas","/upload","/advisory","/simulacion","/simulacion-avanzada",
                  "/create-payment","/update-checklist","/alertas","/fotos"]
    }

# --------------- CARGAS ----------------
@app.get("/cargas")
async def list_cargas():
    return {"cargas": cargas_db}

@app.post("/cargas")
async def create_carga(cliente: str = Form(...), tipo_carga: str = Form(...)):
    carga_id = str(uuid.uuid4())
    carga = {
        "id": carga_id,
        "cliente": cliente,
        "tipo_carga": tipo_carga,
        "estado": "En revisión",
        "alertas": 0,
        "fotos": [],
        "documentos": []
    }
    cargas_db.append(carga)
    return carga

# --------------- UPLOAD FILE ----------------
@app.post("/upload")
async def upload_file(carga_id: str = Form(...), file: UploadFile = File(...), tipo: str = Form(...)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(uploads_dir, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Asociar al carga
    for c in cargas_db:
        if c["id"] == carga_id:
            if tipo.lower() == "foto":
                c["fotos"].append(filename)
            else:
                c["documentos"].append(filename)
            break
    return {"message":"Archivo subido", "filename": filename, "tipo": tipo}

@app.get("/fotos/{filename}")
async def get_photo(filename: str):
    path = os.path.join(uploads_dir, filename)
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"error":"Archivo no encontrado"}, status_code=404)

# --------------- ADVISORY ----------------
@app.post("/advisory")
async def advisory(question: str = Form(...)):
    # respuesta simulada
    return {"data": f"Respuesta a tu consulta: {question} (solo asesoría informativa)"}

# --------------- SIMULACION ----------------
@app.get("/simulacion/{tipo}/{count}")
async def simulacion(tipo: str, count: int):
    riesgo = min(count*10,100)
    return {"tipo": tipo, "riesgo_rechazo": f"{riesgo}%"}

# --------------- ALERTAS ----------------
@app.get("/alertas")
async def get_alertas():
    alertas = []
    for c in cargas_db:
        if c["alertas"]>0:
            alertas.append({"carga_id": c["id"], "nivel": c["alertas"], "mensaje":"Revisar embalaje/documentos"})
    return {"alertas": alertas}

# --------------- CHECKLIST ----------------
@app.post("/update-checklist")
async def update_checklist(carga_id: str = Form(...), estado: str = Form(...)):
    for c in cargas_db:
        if c["id"] == carga_id:
            c["estado"] = estado
            break
    return {"message":"Checklist updated"}

# --------------- PAYMENT SIMULADO ----------------
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    return {"message": f"Pago simulado ${amount/100} - {description}", "url": None}
