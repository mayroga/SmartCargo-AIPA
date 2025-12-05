# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import stripe
import uuid
import os
from typing import List, Dict, Any

# ================= CONFIG =================
BACKEND_MODE = os.getenv("BACKEND_MODE", "free")  # "free" o "pay"
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
stripe.api_key = STRIPE_API_KEY

app = FastAPI(title="SmartCargo-AIPA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # actualizar a tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DATABASE SIMULADO =================
cargas_db: List[Dict[str, Any]] = []
docs_db: List[Dict[str, Any]] = []

# Checklist base
checklist_base = {
    "embalaje": False,
    "pallet_correcto": False,
    "documentos_ok": False,
    "temperatura_ok": False,
    "humedad_ok": False,
    "etiquetado_dg": False,
    "compatibilidad_carga": False,
    "recomendaciones_forwarder": False
}

# Incompatibilidades
incompatibilidades = {
    "DG": ["Perecederos", "Animales Vivos", "Fallecidos"],
    "Perecederos": ["DG", "Químicos"],
    "Animales Vivos": ["DG", "Químicos", "Fallecidos"],
    "Fallecidos": ["Animales Vivos", "DG"],
    "Liquidos": ["Frágil", "DG"]
}

# Riesgo por actor
riesgo_actor = {
    "cliente": 1.0,
    "forwarder": 1.5,
    "transportista": 2.0,
    "handler": 3.0
}

# ================= ROUTES =================
@app.get("/")
def root():
    return {"message": "SmartCargo-AIPA Backend activo", "mode": BACKEND_MODE,
            "routes": ["/cargas", "/upload", "/advisory", "/simulacion", "/simulacion-avanzada", "/create-payment", "/update-checklist", "/alertas"]}

# ================= CARGAS =================
@app.get("/cargas")
async def get_cargas():
    return {"cargas": cargas_db}

@app.post("/cargas")
async def create_carga(cliente: str = Form(...), tipo_carga: str = Form(...), opcion: str = Form("B")):
    carga_id = str(uuid.uuid4())
    nueva_carga = {
        "id": carga_id,
        "cliente": cliente,
        "tipo_carga": tipo_carga,
        "estado": "En revisión",
        "alertas": 0,
        "opcion": opcion,
        "checklist": {},
        "simulaciones": {}
    }
    cargas_db.append(nueva_carga)
    return {"id": carga_id}

# ================= DOCUMENTOS =================
@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    contenido = await file.read()
    docs_db.append({
        "filename": file.filename,
        "size": len(contenido),
        "content_type": file.content_type
    })
    return {"data": {"filename": file.filename}}

# ================= SIMULACION SIMPLE =================
@app.get("/simulacion/{tipo}/{count}")
async def run_simulacion(tipo: str, count: int):
    riesgo = "Bajo"
    if tipo.lower() in ["dg", "animales", "perecederos"] or count > 5:
        riesgo = "Alto"
    elif count > 2:
        riesgo = "Medio"
    return {"riesgo_rechazo": riesgo}

# ================= ADVISORY =================
@app.post("/advisory")
async def advisory(question: Dict[str, str]):
    q = question.get("question","")
    respuesta = f"Respuesta simulada a tu pregunta: {q}. (No somos TSA, solo asesoramos preventivamente)"
    return {"data": respuesta}

# ================= PAGOS =================
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    if BACKEND_MODE == "free":
        return {"message": f"Pago simulado: {description} — Gratis"}
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data":{"currency":"usd","product_data":{"name":description},"unit_amount":amount},"quantity":1}],
            mode="payment",
            success_url="https://smartcargo-advisory.onrender.com/success",
            cancel_url="https://smartcargo-advisory.onrender.com/cancel"
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ================= CHECKLIST Y ALERTAS =================
@app.post("/update-checklist/{carga_id}/{actor}")
async def update_checklist(carga_id: str, actor: str, updates: Dict[str, bool]):
    carga = next((c for c in cargas_db if c["id"] == carga_id), None)
    if not carga:
        return JSONResponse(status_code=404, content={"error": "Carga no encontrada"})

    if "checklist" not in carga:
        carga["checklist"] = {}

    carga["checklist"][actor] = {**checklist_base, **updates}

    alertas = [f"{key} pendiente" for key, val in carga["checklist"][actor].items() if not val]
    carga["alertas"] = len(alertas)
    carga["simulaciones"][actor] = alertas

    return {"checklist": carga["checklist"][actor], "alertas": alertas}

@app.get("/alertas/{carga_id}")
async def get_alertas(carga_id: str):
    carga = next((c for c in cargas_db if c["id"] == carga_id), None)
    if not carga:
        return JSONResponse(status_code=404, content={"error": "Carga no encontrada"})
    return {"alertas_totales": carga.get("alertas", 0), "alertas_por_actor": carga.get("simulaciones", {})}

# ================= SIMULACION AVANZADA =================
@app.post("/simulacion-avanzada/{carga_id}")
async def simulacion_avanzada(carga_id: str):
    carga = next((c for c in cargas_db if c["id"] == carga_id), None)
    if not carga:
        return JSONResponse(status_code=404, content={"error": "Carga no encontrada"})

    tipo_carga = carga.get("tipo_carga", "")
    sim_alertas = {}

    for actor in ["cliente", "forwarder", "transportista", "handler"]:
        actor_alertas = []
        for otras in cargas_db:
            if otras["id"] == carga_id:
                continue
            otras_tipo = otras.get("tipo_carga", "")
            if tipo_carga in incompatibilidades and otras_tipo in incompatibilidades[tipo_carga]:
                actor_alertas.append(f"Incompatible con carga ID {otras['id']} ({otras_tipo})")
        riesgo_total = len(actor_alertas) * riesgo_actor[actor]
        actor_alertas.append(f"Nivel de riesgo estimado: {riesgo_total}")
        sim_alertas[actor] = actor_alertas

    carga["simulaciones"]["avanzada"] = sim_alertas
    return {"simulacion_avanzada": sim_alertas}
