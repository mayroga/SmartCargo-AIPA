import os
import stripe
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class CargoInput(BaseModel):
    awb: str; length_cm: float; width_cm: float; height_cm: float
    weight_declared: float; dg_type: str; ispm15_seal: str

@app.post("/cargas")
async def validate_cargo(cargo: CargoInput):
    alerts = []
    score = 0
    
    # CÁLCULOS TÉCNICOS
    volumen_m3 = (cargo.length_cm * cargo.width_cm * cargo.height_cm) / 1_000_000
    peso_volumetrico = (cargo.length_cm * cargo.width_cm * cargo.height_cm) / 6000
    
    # REGLAS DE RIESGO
    if cargo.height_cm > 160: alerts.append("Altura crítica (>160cm). No apto para ULD estándar."); score += 30
    if peso_volumetrico > cargo.weight_declared: alerts.append("Cobro por Peso Volumétrico aplicable."); score += 10
    if cargo.ispm15_seal == "NO": alerts.append("Falta Certificado ISPM-15. Riesgo fitosanitario alto."); score += 40
    if cargo.dg_type != "NONE": alerts.append("Carga Especial Detectada. Requiere revisión de etiquetas."); score += 20

    return {
        "alertaScore": min(score, 100),
        "alerts": alerts,
        "volumen": f"{volumen_m3:.3f} m3",
        "peso_vol": f"{peso_volumetrico:.2f}"
    }

@app.post("/advisory")
async def advisory(prompt: str = Form(...), image: UploadFile = File(None)):
    contents = [prompt]
    if image:
        img_bytes = await image.read()
        contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
    
    response = client_gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction="Eres SMARTCARGO CONSULTING. Experto bilingüe IATA. Solo asesoría. Termina siempre con: 'Verifique con manuales oficiales'."
        )
    )
    return {"data": response.text}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: str = Form(None), password: str = Form(None)):
    if user == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
        return {"url": f"?access=granted&awb={awb}"}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Auditoría {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}",
        cancel_url=f"https://smartcargo-aipa.onrender.com/index.html"
    )
    return {"url": session.url}
