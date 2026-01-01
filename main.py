import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# --- BLINDAJE CORS: PERMITIR QUE EL FRONTEND HABLE CON EL BACKEND ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://smartcargo-advisory.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY")

@app.post("/advisory")
async def get_advisory(prompt: str = Form(...), lang: str = Form("es"), images: List[UploadFile] = File(None)):
    instruction = (
        f"Eres SMARTCARGO CONSULTING. Responde en {lang}. "
        "Da múltiples soluciones legales (TSA/IATA). "
        "ORDEN: 1. Más BARATA y RÁPIDA. 2. Intermedia. 3. Cara/Estructural."
    )
    
    # Prioridad 1: Gemini para fotos
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            parts = [{"text": f"{instruction}\n\nConsulta: {prompt}"}]
            if images:
                for img in images[:3]:
                    content = await img.read()
                    if content: parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    # Prioridad 2: OpenAI de Respaldo
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error técnico: {e}"}

    return {"data": "Servicio de IA temporalmente no disponible."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    # Redirige de vuelta al FRONTEND
    success_url = f"https://smartcargo-advisory.onrender.com/index.html?access=granted&awb={awb}"
    
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}
    
    stripe.api_key = STRIPE_SECRET
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Asesoría AWB: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}
