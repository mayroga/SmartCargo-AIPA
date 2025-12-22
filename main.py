import os
import stripe
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import stripe
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI(title="SmartCargo-AIPA Backend")

# --- VARIABLES DE ENTORNO ---
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "secret123")
FRONTEND_URL = "https://smartcargo-advisory.onrender.com"
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CargoInput(BaseModel):
    awb: str
    content: str
    height_cm: float
    weight_declared: float
    packing_integrity: str
    ispm15_seal: str
    dg_type: str
    weight_match: str

@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...), 
    description: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # 1. LOGICA DE BYPASS ADMIN
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {
            "url": f"{FRONTEND_URL}/success.html?access=granted",
            "message": "Bypass Admin Activado"
        }

    # 2. LOGICA DE COBRO REAL STRIPE
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': description},
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{FRONTEND_URL}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/cancel.html",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "AIPA Operational"}
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str

@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    
    # NORMALIZACIÓN A MÉTRICO PARA CÁLCULO IATA
    L, W, H, WG = cargo.length, cargo.width, cargo.height, cargo.weight
    
    if cargo.unit_system == "in":
        L_cm, W_cm, H_cm = L * 2.54, W * 2.54, H * 2.54
        WG_kg = WG / 2.205
        factor_vol = 166 # Factor IATA para pulgadas
    else:
        L_cm, W_cm, H_cm = L, W, H
        WG_kg = WG
        factor_vol = 6000 # Factor IATA para CM

    vol_m3 = (L_cm * W_cm * H_cm) / 1_000_000
    peso_v = (L * W * H) / factor_vol

    # REGLAS TÉCNICAS
    if H_cm > 158:
        alerts.append("Altura crítica. No apto para ULD estándar. / Excessive height.")
        score += 35
    if cargo.ispm15_seal == "NO":
        alerts.append("Madera sin sello. Use Plástico/Cartón. / Wood no seal. Use Plastic.")
        score += 40
    
    details = f"{vol_m3:.3f} m3 | Vol-Weight: {peso_v:.2f}"
    return {"score": min(score, 100), "alerts": alerts, "details": details}

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: UploadFile = File(None)):
    contents = [prompt]
    if image:
        img_bytes = await image.read()
        contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
    
    res = client_gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction="Eres SMARTCARGO CONSULTING. Experto bilingüe. Responde técnico y breve. Máximo 3 respuestas por sesión. Termina con: Asesoría técnica informativa.",
            max_output_tokens=350
        )
    )
    return {"data": res.text}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Audit {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url="https://smartcargo-aipa.onrender.com/index.html"
    )
    return {"url": session.url}
