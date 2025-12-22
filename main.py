import os
import stripe
import base64
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

load_dotenv()

# --- CONFIGURACIÓN DE CONTROL ---
FREE_ACCESS = True  # True: Modo Asesor Libre / False: Requiere Pago Stripe
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "smart2025")
FRONTEND_URL = "https://smartcargo-aipa.onrender.com"

app = FastAPI(title="SmartCargo-AIPA Global Advisor")

# Clientes de IA con Blindaje Dual
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str; pkg_type: str

# 1. MOTOR DE AUDITORÍA TÉCNICA
@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    alerts = []
    score = 0
    is_in = cargo.unit_system == "in"
    H_cm = cargo.height * 2.54 if is_in else cargo.height
    
    # Lógica de Seguridad y Eficiencia
    if H_cm > 158:
        alerts.append("CRITICAL HEIGHT: Exceeds 158cm. Fuselage Contour Risk. / RIESGO DE CONTORNO: Excede 158cm.")
        score += 40
    if cargo.ispm15_seal == "NO":
        alerts.append("BIO-HAZARD: No ISPM-15 wood seal. Potential Seizure. / RIESGO FITOSANITARIO: Sin sello NIMF-15.")
        score += 30
    if cargo.pkg_type in ["Drum", "Crate"] and H_cm > 120:
        alerts.append("STABILITY ALERT: High center of gravity for " + cargo.pkg_type)
        score += 15

    vol_m3 = ((cargo.length * (2.54 if is_in else 1)) * (cargo.width * (2.54 if is_in else 1)) * (cargo.height * (2.54 if is_in else 1))) / 1_000_000
    peso_v = (cargo.length * cargo.width * cargo.height) / (166 if is_in else 6000)
    
    return {"score": min(score, 100), "alerts": alerts, "details": f"{vol_m3:.3f} m³ | V-Weight: {peso_v:.2f}"}

# 2. ASESOR IA (MATANDO NECESIDADES TÉCNICAS)
@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    img_bytes = await image.read() if image else None
    
    instruction = """
    ERES EL ASESOR TÉCNICO SENIOR DE SMARTCARGO AIPA. TU OBJETIVO ES SOLUCIONAR, NO SOLO REPORTAR.
    Bases de conocimiento: IATA DGR, TSA Security, Aircraft Loading.
    REGLAS DE ORO:
    - SKIDS/CRATES: Revisa integridad de base y zunchado (strapping).
    - DRUMS: Detecta abolladuras en bordes o fugas.
    - DG/LABELS: Etiquetas SIEMPRE hacia afuera. Si no las ves, alerta de RECHAZO.
    - APILAMIENTO: Identifica cajas aplastadas por mal ahorro de espacio.
    - BLINDAJE: Eres asesor. Da recomendaciones técnicas para que la carga pase el counter.
    RESPUESTA: Técnica, directa, bilingüe (EN/ES).
    """

    try:
        # Intento con Gemini
        contents = [prompt]
        if img_bytes:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        res = client_gemini.models.generate_content(
            model="gemini-2.0-flash", contents=contents,
            config=types.GenerateContentConfig(system_instruction=instruction, max_output_tokens=500)
        )
        return {"data": res.text, "provider": "gemini"}
    except:
        # Failover a OpenAI
        try:
            messages = [{"role": "system", "content": instruction}]
            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode('utf-8')
                messages.append({"role": "user", "content": [{"type":"text","text":prompt}, {"type":"image_url","image_url":{"url":f"data:{image.content_type};base64,{b64}"}}]})
            else:
                messages.append({"role": "user", "content": prompt})
            res = client_openai.chat.completions.create(model="gpt-4o", messages=messages)
            return {"data": res.choices[0].message.content, "provider": "openai"}
        except Exception as e:
            return {"data": f"Technical Service Temporarily Unavailable: {str(e)}"}

# 3. GESTIÓN DE PAGOS Y ACCESO
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    target = f"{FRONTEND_URL}/index.html?access=granted&awb={awb}"
    if FREE_ACCESS or (user == ADMIN_USER and password == ADMIN_PASS):
        return {"url": target}
    
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price_data':{'currency':'usd','product_data':{'name':f"Technical Audit AWB {awb}"},'unit_amount':int(amount*100)},'quantity':1}],
        mode='payment', success_url=target, cancel_url=f"{FRONTEND_URL}/index.html"
    )
    return {"url": session.url}

@app.get("/config")
async def get_config(): return {"free_mode": FREE_ACCESS, "status": "Ready"}
