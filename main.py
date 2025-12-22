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
# ACCESO GLOBAL: True = GRATIS / False = COBRO ACTIVO
# =====================================================
FREE_ACCESS = True  
# =====================================================

app = FastAPI(title="SmartCargo-AIPA Final")

# Clientes de IA
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

# AUDITORÍA TÉCNICA
@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    is_in = cargo.unit_system == "in"
    
    # Conversión para lógica de alertas
    H_cm = cargo.height * 2.54 if is_in else cargo.height
    
    # Factor IATA
    vol_m3 = ((cargo.length * (2.54 if is_in else 1)) * (cargo.width * (2.54 if is_in else 1)) * (cargo.height * (2.54 if is_in else 1))) / 1_000_000
    
    peso_v = (cargo.length * cargo.width * cargo.height) / (166 if is_in else 6000)

    if H_cm > 158:
        alerts.append("CRITICAL HEIGHT: >158cm. High risk of rejection for Narrow Body / ALTURA CRÍTICA.")
        score += 35
    if cargo.ispm15_seal == "NO":
        alerts.append("ISPM-15 RISK: No wood seal detected / RIESGO FITOSANITARIO.")
        score += 40
    
    return {"score": min(score, 100), "alerts": alerts, "details": f"{vol_m3:.3f} m³ | V-Weight: {peso_v:.2f}"}

# ASESOR IA (FALLBACK AUTOMÁTICO)
@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    img_bytes = await image.read() if image else None
    instruction = "You are SMARTCARGO AI. Technical, brief, bilingual (EN/ES). Direct answers only."

    # Intento 1: Gemini
    try:
        contents = [prompt]
        if img_bytes:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        res = client_gemini.models.generate_content(
            model="gemini-2.0-flash", contents=contents,
            config=types.GenerateContentConfig(system_instruction=instruction, max_output_tokens=350)
        )
        return {"data": res.text}
    except:
        # Intento 2: OpenAI
        try:
            msgs = [{"role": "system", "content": instruction}]
            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode('utf-8')
                msgs.append({"role": "user", "content": [{"type":"text","text":prompt}, {"type":"image_url","image_url":{"url":f"data:{image.content_type};base64,{b64}"}}]})
            else:
                msgs.append({"role": "user", "content": prompt})
            res = client_openai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=350)
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": "System Busy. Please try again. / Sistema ocupado."}

# PAGOS Y ACCESO
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...),
                         user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    
    url_success = f"{FRONTEND_URL}/index.html?access=granted&awb={awb}"
    
    if FREE_ACCESS or (user == ADMIN_USER and password == ADMIN_PASS):
        return {"url": url_success}

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f"Audit: {awb}"}, 'unit_amount': int(amount * 100)}, 'quantity': 1}],
        mode='payment', success_url=url_success, cancel_url=f"{FRONTEND_URL}/index.html"
    )
    return {"url": session.url}

@app.get("/health")
async def health(): return {"status": "online", "free_mode": FREE_ACCESS}
