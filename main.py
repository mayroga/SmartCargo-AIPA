import os
import stripe
import base64
import httpx
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

load_dotenv()

# =====================================================
# CONFIGURACIÓN DE ACCESO (EL INTERRUPTOR)
# =====================================================
FREE_ACCESS = True  # <--- CAMBIA A "False" PARA ACTIVAR COBROS DE STRIPE
# =====================================================

app = FastAPI(title="SmartCargo-AIPA Backend")

client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "secret123")
FRONTEND_URL = "https://smartcargo-aipa.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str

@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    is_in = cargo.unit_system == "in"
    L_cm = cargo.length * 2.54 if is_in else cargo.length
    H_cm = cargo.height * 2.54 if is_in else cargo.height
    W_cm = cargo.width * 2.54 if is_in else cargo.width
    
    vol_m3 = (L_cm * W_cm * H_cm) / 1_000_000
    peso_v = (cargo.length * cargo.width * cargo.height) / (166 if is_in else 6000)

    if H_cm > 158:
        alerts.append("ALTURA CRÍTICA: Supera 158cm. / Height alert.")
        score += 35
    if cargo.ispm15_seal == "NO":
        alerts.append("RIESGO MADERA: Sin sello ISPM-15. / Wood no seal.")
        score += 40
    
    return {"score": min(score, 100), "alerts": alerts, "details": f"{vol_m3:.3f} m³ | Vol-W: {peso_v:.2f}"}

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    img_bytes = await image.read() if image else None
    
    # Failover Gemini -> OpenAI
    try:
        contents = [prompt]
        if img_bytes:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        res = client_gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction="Eres SMARTCARGO. Responde breve y técnico.", max_output_tokens=350)
        )
        return {"data": res.text}
    except:
        try:
            messages = [{"role": "system", "content": "Eres SMARTCARGO. Responde breve."}]
            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode('utf-8')
                messages.append({"role": "user", "content": [{"type":"text","text":prompt}, {"type":"image_url","image_url":{"url":f"data:{image.content_type};base64,{b64}"}}]})
            else:
                messages.append({"role": "user", "content": prompt})
            response = client_openai.chat.completions.create(model="gpt-4o", messages=messages, max_tokens=350)
            return {"data": response.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error: {str(e)}"}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...),
                         user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    
    # 1. SI EL MODO FREE ESTÁ ACTIVO, REDIRIGIR DIRECTO
    if FREE_ACCESS:
        return {"url": f"{FRONTEND_URL}/index.html?access=granted&awb={awb}", "mode": "free"}

    # 2. BYPASS ADMIN
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{FRONTEND_URL}/index.html?access=granted&awb={awb}", "mode": "admin"}

    # 3. PAGO STRIPE (CLIENTES)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f"Audit AWB: {awb}"}, 'unit_amount': int(amount * 100)}, 'quantity': 1}],
        mode='payment',
        success_url=f"{FRONTEND_URL}/index.html?access=granted&awb={awb}",
        cancel_url=f"{FRONTEND_URL}/index.html"
    )
    return {"url": session.url}

# Nueva ruta para que el frontend sepa si es gratis
@app.get("/config")
async def get_config():
    return {"free_mode": FREE_ACCESS}
