from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

app = FastAPI(title="SmartCargo-AIPA Backend")

# ================= CONFIG =================
BACKEND_MODE = "free"  # cambiar a "pay" para activar cobro real

# ================= CORS =================
origins = [
    "https://smartcargo-advisory.onrender.com",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROOT =================
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h2>SmartCargo-AIPA backend activo ✅</h2>
    <p>Modo actual: {}</p>
    <p>Rutas: /cargas, /upload, /advisory, /simulacion, /create-payment</p>
    """.format(BACKEND_MODE)

# ================= CARGAS =================
cargas_store = []

@app.get("/cargas")
def get_cargas():
    return {"cargas": cargas_store}

@app.post("/cargas")
def create_carga(carga: dict):
    carga_id = len(cargas_store) + 1
    carga["id"] = carga_id
    cargas_store.append(carga)
    return {"id": carga_id, "message": "Carga creada"}

# ================= UPLOAD =================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    return {"data": {"filename": filename, "status": "uploaded"}}

# ================= SIMULACION =================
@app.get("/simulacion/{tipo}/{count}")
def simulacion(tipo: str, count: int):
    riesgo = min(count * 10, 100)
    return {"tipo": tipo, "riesgo_rechazo": f"{riesgo}%"}

# ================= ADVISORY =================
@app.post("/advisory")
def advisory(question: dict):
    q = question.get("question", "")
    return {"data": f"Respuesta de AIPA simulada para: {q}"}

# ================= PAYMENTS =================
@app.post("/create-payment")
def create_payment(amount: int = Form(...), description: str = Form(...)):
    if BACKEND_MODE == "free":
        return {"message": f"Pago simulado: {description} — Gratis"}
    # Aquí iría la integración real con Stripe cuando BACKEND_MODE="pay"
    return {"message": f"Pago real activado para: {description}"}
