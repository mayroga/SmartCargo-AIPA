from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime

# =====================================================
# CONFIGURACIÓN BÁSICA
# =====================================================
app = FastAPI(title="SmartCargo-AIPA Backend")

# Permitir que el frontend en Render acceda
origins = [
    "https://smartcargo-advisory.onrender.com",  # tu sitio estático
    "*",  # opcional, para pruebas
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# VARIABLES DE ENTORNO
# =====================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY no configurada. /advisory no funcionará correctamente.")

# =====================================================
# MOCK DATABASE
# =====================================================
cargas_db = []
documents_db = []
alertas_db = []
fotos_db = []

# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/")
async def root():
    return {
        "message": "SmartCargo-AIPA Backend activo",
        "mode": "free",
        "routes": ["/cargas","/upload","/advisory","/simulacion","/simulacion-avanzada","/create-payment","/update-checklist","/alertas"]
    }

# ------------------ CARGAS ------------------
@app.get("/cargas")
async def get_cargas():
    return {"cargas": cargas_db}

@app.post("/cargas")
async def create_carga(payload: dict):
    carga_id = str(uuid.uuid4())
    carga = {
        "id": carga_id,
        "cliente": payload.get("cliente"),
        "tipo_carga": payload.get("tipo_carga"),
        "estado": "En revisión",
        "alertas": 0,
        "fecha_creacion": str(datetime.utcnow())
    }
    cargas_db.append(carga)
    return {"id": carga_id}

# ------------------ DOCUMENTOS ------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"uploads/{filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    documents_db.append({"id": str(uuid.uuid4()), "filename": filename, "fecha_subida": str(datetime.utcnow())})
    return {"data": {"filename": filename}}

# ------------------ ADVISORY ------------------
@app.post("/advisory")
async def advisory(question: str = Form(...)):
    if not GEMINI_API_KEY:
        return JSONResponse({"error":"GEMINI_API_KEY no configurada"}, status_code=500)

    # Simulación de respuesta usando la clave
    respuesta = f"Simulación: respuesta para '{question}' usando GEMINI_API_KEY configurada."
    return {"data": respuesta}

# ------------------ SIMULACION ------------------
@app.get("/simulacion/{tipo}/{count}")
async def run_simulation(tipo: str, count: int):
    riesgo = min(count * 10, 100)  # cálculo de riesgo simplificado
    return {"riesgo_rechazo": f"{riesgo}%"}

# ------------------ CREATE PAYMENT ------------------
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    # Simulación de creación de pago Stripe
    payment_url = f"https://stripe.com/pay/simulated?amount={amount}&desc={description}"
    return {"url": payment_url, "message": "Simulated payment link"}

# ------------------ ALERTAS ------------------
@app.get("/alertas")
async def get_alertas():
    return {"alertas": alertas_db}

# ------------------ UPDATE CHECKLIST ------------------
@app.post("/update-checklist")
async def update_checklist(payload: dict):
    # Simulación de actualización de checklist
    return {"message": "Checklist updated", "data": payload}

# =====================================================
# INSTRUCCIONES ADICIONALES
# =====================================================
# 1. Asegúrate de tener la variable de entorno GEMINI_API_KEY en Render.
# 2. Subir la carpeta uploads/ en caso de usar documentos o fotos.
# 3. Frontend debe apuntar a BACKEND_URL = "https://smartcargo-aipa.onrender.com"
