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

app = FastAPI(title="SmartCargo-AIPA Backend")

# --- CLIENTES DE IA ---
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- CONFIGURACIÓN ---
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
FRONTEND_URL = "https://smartcargo-aipa.onrender.com"

stripe.api_key = STRIPE_KEY

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str

# --- 1. AUDITORÍA TÉCNICA ---
@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    L, W, H = cargo.length, cargo.width, cargo.height
    is_in = cargo.unit_system == "in"
    
    H_cm = H * 2.54 if is_in else H
    L_cm = L * 2.54 if is_in else L
    W_cm = W * 2.54 if is_in else W
    
    vol_m3 = (L_cm * W_cm * H_cm) / 1_000_000
    peso_v = (L * W * H) / (166 if is_in else 6000)

    if H_cm > 158:
        alerts.append("ALTURA CRÍTICA: >158cm. No apto para Narrow Body. / Height alert.")
        score += 35
    if cargo.ispm15_seal == "NO":
        alerts.append("RIESGO MADERA: Sin sello ISPM-15. / Wood no seal.")
        score += 40
    
    return {"score": min(score, 100), "alerts": alerts, "details": f"{vol_m3:.3f} m³ | Vol-W: {peso_v:.2f}"}

# --- 2. ASESOR IA (FAILOVER: GEMINI -> OPENAI) ---
@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    img_bytes = await image.read() if image else None
    
    # INTENTO 1: GEMINI
    try:
        contents = [prompt]
        if img_bytes:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        
        res = client_gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Eres SMARTCARGO CONSULTING. Responde breve y técnico. Bilingüe.",
                max_output_tokens=350
            )
        )
        return {"data": res.text, "provider": "gemini"}

    except Exception as e:
        print(f"Gemini falló, intentando OpenAI... Error: {e}")
        
        # INTENTO 2: OPENAI (Failover)
        try:
            messages = [{"role": "system", "content": "Eres SMARTCARGO CONSULTING. Responde breve y técnico."}]
            
            if img_bytes:
                # OpenAI requiere la imagen en Base64 dentro del mensaje
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{image.content_type};base64,{base64_image}"}}
                    ]
                })
            else:
                messages.append({"role": "user", "content": prompt})

            response = client_openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=350
            )
            return {"data": response.choices[0].message.content, "provider": "openai"}
        
        except Exception as e2:
            return {"data": f"Error crítico en ambos servicios: {str(e2)}"}

# --- 3. PAGOS + BYPASS ---
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...),
                         user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{FRONTEND_URL}/index.html?access=granted&awb={awb}"}

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f"Audit {awb}"}, 'unit_amount': int(amount * 100)}, 'quantity': 1}],
        mode='payment',
        success_url=f"{FRONTEND_URL}/index.html?access=granted&awb={awb}",
        cancel_url=f"{FRONTEND_URL}/index.html"
    )
    return {"url": session.url}
