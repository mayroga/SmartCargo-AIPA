import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- VARIABLES DESDE TU RENDER ---
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK = os.getenv("STRIPE_WEBHOOK_SECRET")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "Admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "Pass")

stripe.api_key = STRIPE_SECRET

@app.post("/advisory")
async def get_advisory(prompt: str = Form(...), lang: str = Form("es"), images: List[UploadFile] = File(None)):
    instruction = (
        f"Eres SMARTCARGO CONSULTING. Responde en {lang}. "
        "Da múltiples soluciones legales según TSA e IATA. "
        "ORDEN: 1. Rápida/Barata. 2. Media. 3. Cara/Estructural."
    )
    
    # Motor 1: Gemini (Principal para fotos)
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
        except Exception: pass

    # Motor 2: OpenAI (Respaldo)
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

    return {"data": "Sistemas de IA no disponibles."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    # Redirección de éxito
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    
    # VALIDACIÓN DE ADMINISTRADOR (Blindaje)
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}
    
    # PAGO CON STRIPE
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Asesoría SmartCargo AWB: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=success_url
        )
        return {"url": session.url}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def home(): return FileResponse("index.html")

app.mount("/", StaticFiles(directory=".", html=True), name="static")
