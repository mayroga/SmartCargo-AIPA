from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import uvicorn
import os
import uuid
import shutil

app = FastAPI(title="SmartCargo-AIPA Backend")

# ================== CORS ==================
origins = ["*"]  # Ajusta si quieres limitar dominios
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== DATA ==================
cargas_db = []  # Lista de cargas
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)

# ================== ROUTES ==================
@app.get("/")
async def root():
    return {"message":"SmartCargo-AIPA Backend activo",
            "mode":"free",
            "routes":["/cargas","/upload","/advisory","/simulacion","/simulacion-avanzada",
                      "/create-payment","/update-checklist","/alertas"]}

# ------------------ CARGAS ------------------
@app.get("/cargas")
async def list_cargas():
    return {"cargas": cargas_db}

@app.post("/cargas")
async def create_carga(cliente: str = Form(...), tipo_carga: str = Form(...)):
    carga_id = str(uuid.uuid4())
    carga = {"id": carga_id, "cliente": cliente, "tipo_carga": tipo_carga, "estado": "En revisión", "alertas":0, "files":[]}
    cargas_db.append(carga)
    return carga

# ------------------ UPLOAD ------------------
@app.post("/upload")
async def upload_file(carga_id: str = Form(...), file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(uploads_dir, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Asociar al carga
    for c in cargas_db:
        if c["id"] == carga_id:
            c["files"].append(filename)
            break
    return {"message":"File uploaded","filename":filename}

# ------------------ ADVISORY ------------------
@app.post("/advisory")
async def advisory(question: str = Form(...)):
    # Respuesta simulada
    return {"data": f"Respuesta a tu consulta: {question} (solo asesoría informativa)"}

# ------------------ SIMULACION ------------------
@app.get("/simulacion/{tipo}/{count}")
async def simulacion(tipo: str, count: int):
    riesgo = min(count * 10, 100)  # Simulación simple
    return {"tipo": tipo, "riesgo_rechazo": f"{riesgo}%"}

# ------------------ CREATE PAYMENT ------------------
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    # Simulación de pago
    return {"message": f"Pago simulado por ${amount/100} - {description}", "url": None}

# ------------------ ALERTAS ------------------
@app.get("/alertas")
async def get_alertas():
    alertas = [{"carga_id": c["id"], "alertas": c["alertas"]} for c in cargas_db]
    return {"alertas": alertas}

# ------------------ UPDATE CHECKLIST ------------------
@app.post("/update-checklist")
async def update_checklist(carga_id: str = Form(...), estado: str = Form(...)):
    for c in cargas_db:
        if c["id"] == carga_id:
            c["estado"] = estado
            break
    return {"message":"Checklist updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
