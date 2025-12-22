import os
import stripe
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from google import genai
from google.genai import types

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# CONFIGURACIÓN ESTRATÉGICA IA
SYSTEM_PROMPT = (
    "Eres SMARTCARGO CONSULTING. Experto bilingüe IATA/Logística. "
    "Tu estilo: CONCISO Y TÉCNICO. Da SOLUCIONES inmediatas (Ej: si no hay madera certificada, sugiere plástico/cartón). "
    "No te extiendas. Responde en el idioma del usuario. "
    "Obligatorio terminar: 'Asesoría informativa. Consulte manuales oficiales'."
)

class CargoInput(BaseModel):
    awb: str; length_cm: float; width_cm: float; height_cm: float
    weight_declared: float; dg_type: str; ispm15_seal: str

@app.post("/cargas")
async def validate_cargo(cargo: CargoInput):
    alerts = []
    score = 0
    vol = (cargo.length_cm * cargo.width_cm * cargo.height_cm) / 1_000_000
    peso_v = (cargo.length_cm * cargo.width_cm * cargo.height_cm) / 6000

    if cargo.ispm15_seal == "NO":
        alerts.append("RIESGO FITOSANITARIO: Madera sin sello. SOLUCIÓN: Cambie a paletas de PLÁSTICO o CARTÓN.")
        score += 40
    if cargo.height_cm > 158:
        alerts.append("ALTURA EXCEDIDA: No apto para ULD estándar. SOLUCIÓN: Bajar altura a <158cm.")
        score += 30
    if cargo.dg_type != "NONE":
        alerts.append("CARGA ESPECIAL: Requiere etiquetas IATA específicas y Shippers Declaration.")
        score += 20
        
    return {"alertaScore": min(score, 100), "alerts": alerts, "volumen": f"{vol:.3f} m3", "peso_vol": f"{peso_v:.2f}"}

@app.post("/advisory")
async def advisory(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    contents = [prompt]
    if image:
        img_bytes = await image.read()
        contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
    
    response = client_gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, max_output_tokens=350)
    )
    return {"data": response.text}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    # URL de retorno dinámica para Render
    base_url = "https://smartcargo-aipa.onrender.com"
    success_url = f"{base_url}/index.html?access=granted&awb={awb}"
    
    if user == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
        return {"url": success_url}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"SmartCargo Audit: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url=f"{base_url}/index.html"
    )
    return {"url": session.url}
