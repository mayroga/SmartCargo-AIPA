# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, json, uuid

# ================= CONFIG =================
BACKEND_MODE = os.getenv("BACKEND_MODE","free")  # Cambiar a "pay" para activar cobro
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY","sk_test_xxx")  # tu clave Stripe
FRONTEND_URL = os.getenv("FRONTEND_URL","https://yourfrontend.com")  # para checkout redirect
FRONTEND_ORIGINS = ["*"]  # en producción ajustar al dominio real

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
    os.makedirs("uploads", exist_ok=True)
    filename = f"uploads/{file.filename}"
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
    answer = f"Respuesta simulada a: {q[:200]}"
    return {"data": answer}

# ================= STRIPE PAYMENT =================
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    if BACKEND_MODE=="free":
        # Simulación gratis
        return {"message": f"Simulación de pago exitosa: {description} — Gratis"}

    # Pago real con Stripe
    import stripe
    stripe.api_key = STRIPE_API_KEY
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': description},
                    'unit_amount': amount  # en centavos
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=f"{FRONTEND_URL}/success",
            cancel_url=f"{FRONTEND_URL}/cancel"
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)
