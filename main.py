import os
import stripe
import base64
import openai
import google.generativeai as genai  # Librería estable
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv

# 1. Cargar variables de entorno
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 2. Configurar Gemini con la versión estable
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None) # Debe coincidir con el nombre en app.js
):
    # Instrucciones de experto en inspección
    instruction = (
        f"Answer in {lang}. You are a Visual Inspection Expert for SMARTCARGO. "
        "Analyze images in detail: read text, identify objects and cargo status. "
        "If no images, ask the user to upload photos for a better plan. "
        "Use 🔴 [ALERT] or 🟢 [COMPLIANCE] and give an 'Action Plan'."
    )

    # Preparamos la lista de partes para enviar a Gemini
    # Empezamos con el texto de instrucción y el problema del cliente
    prompt_parts = [instruction, f"\n\nClient Issue: {prompt}"]

    # 3. Procesamos las fotos de forma estable
    if files:
        for f in files:
            content = await f.read()
            if content:
                # Convertimos la foto al formato que la librería estable entiende
                prompt_parts.append({
                    "mime_type": f.content_type,
                    "data": content
                })

    try:
        # Generamos el contenido
        response = model.generate_content(prompt_parts)
        return {"data": response.text}

    except Exception as e:
        print(f"Error en Gemini: {e}")
        return {"data": "Lo siento, hubo un problema al procesar la visión. Intenta con fotos más pequeñas o formato JPG."}

# --- RUTA DE PAGOS (Mantén la que ya tienes) ---
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
        return {"url": f"/?access=granted&awb={awb}"}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"AWB: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}",
        cancel_url=f"https://smartcargo-aipa.onrender.com/"
    )
    return {"url": session.url}
