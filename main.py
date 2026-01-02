import os
import stripe
import base64
import openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Cargar variables primero
load_dotenv()

app = FastAPI()

# Seguridad para el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- VARIABLES DE ENTORNO ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# 2. Inicializar cliente de Google una sola vez
# Usamos el KEY del entorno, no "YOUR_API_KEY"
client_gemini = genai.Client(api_key=GEMINI_KEY)

# --- RUTAS BÁSICAS ---
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js")

# --- MOTOR DE ASESORAMIENTO ---
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None) # Nombre 'files' para coincidir con el JS
):
    instruction = (
        f"You are the Senior Technical Advisor for SMARTCARGO. Answer in {lang}. "
        "MISSION: Provide 'Action Plans' to pass inspections. "
        "LEGAL: Technical suggestions only, not a legal verdict. "
        "Identify risks with 🔴 [ALERT] or 🟢 [COMPLIANCE]. Never mention AI."
    )

    # --- 1. INTENTO CON GEMINI (SDK Oficial) ---
    if GEMINI_KEY:
        try:
            # Preparamos los contenidos (Texto + Fotos)
            contents = [instruction, f"Client Issue: {prompt}"]
            
            if files:
                for img in files[:5]: # Máximo 5 fotos
                    content = await img.read()
                    if content:
                        contents.append(
                            types.Part.from_bytes(data=content, mime_type=img.content_type)
                        )

            response = client_gemini.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents
            )
            return {"data": response.text}

        except Exception as e:
            print(f"Error en Gemini SDK: {e}")
            # Si falla Gemini, el código sigue hacia OpenAI abajo

    # --- 2. RESPALDO OPENAI ---
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error en sistema de respaldo: {str(e)}"}

    return {"data": "System busy. Try again later."}

# --- PAGOS (Completado) ---
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # Bypass para Administrador
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={awb}"}

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Advisory AWB: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}",
            cancel_url=f"https://smartcargo-aipa.onrender.com/",
        )
        return {"url": session.url}
    except Exception as e:
        return {"error": str(e)}
