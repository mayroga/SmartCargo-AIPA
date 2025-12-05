# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import os, json, uuid

# ================= CONFIG =================
BACKEND_MODE = os.getenv("BACKEND_MODE","free")  # cambiar a "pay" para activar cobro
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY","sk_test_xxx")
FRONTEND_ORIGINS = ["*"]  # Ajustar a dominios permitidos en producción

# ================= APP =================
app = FastAPI(title="SmartCargo-AIPA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DUMMY DATA =================
CARGAS_DB = []
DOCS_DB = []

# ================= HELPERS =================
def gen_id():
    return str(uuid.uuid4())[:8]

# ================= ROUTES =================

@app.get("/cargas")
def list_cargas():
    return {"cargas": CARGAS_DB}

@app.post("/cargas")
def create_carga(payload: dict):
    carga_id = gen_id()
    payload['id'] = carga_id
    CARGAS_DB.append(payload)
    return {"id": carga_id}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(filename,"wb") as f:
        f.write(await file.read())
    DOCS_DB.append({"filename": file.filename, "path": filename})
    return {"data":{"filename":file.filename}}

@app.get("/simulacion/{tipo}/{count}")
def simulacion(tipo:str,count:int):
    riesgo = "Alto" if count>3 else "Medio" if count>0 else "Bajo"
    return {"tipo":tipo,"count":count,"riesgo_rechazo":riesgo}

@app.post("/advisory")
async def advisory_endpoint(payload: dict):
    q = payload.get("question","")
    # Respuesta dummy
    answer = f"Respuesta simulada a: {q[:200]}"
    return {"data": answer}

@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    if BACKEND_MODE=="free":
        return {"message": f"Simulación de pago exitosa: {description} — Gratis"}
    # Stripe real
    import stripe
    stripe.api_key = STRIPE_API_KEY
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data':{'currency':'usd','product_data':{'name':description},'unit_amount':amount},'quantity':1}],
            mode='payment',
            success_url="https://yourfrontend.com/success",
            cancel_url="https://yourfrontend.com/cancel"
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)
