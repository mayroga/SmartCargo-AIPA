import os
import stripe
import httpx
import base64
import openai
import io
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv
from PIL import Image, ImageOps
from google import genai

# 1. Cargar variables de entorno
load_dotenv()

app = FastAPI()

# 2. Configuración de Seguridad (CORS)
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

# --- RUTAS DE ARCHIVOS (Frontend) ---
@app.get("/")
async def home():
    return FileResponse("index.html", media_type="text/html")

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js", media_type="application/javascript")

# --- MOTOR DE ASESORAMIENTO ---
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    instruction = (
        f"You are the Senior Technical Advisor for SMARTCARGO by MAY ROGA LLC. Answer in {lang}. "
        "MISSION: Be a practical solver. Provide 'Action Plans' to pass inspections immediately. "
        "LEGAL SHIELD: We are PRIVATE ADVISORS. Technical suggestions only. "
        "Identify risks with [ALERT] or [COMPLIANCE]. Never mention AI."
    )

    parts = [{"text": f"{instruction}\n\nClient Issue: {prompt}"}]

    if GEMINI_KEY:
        try:
            if files:
                for img in files[:3]:
                    content = await img.read()
                    if content:
                        encoded = base64.b64encode(content).decode("utf-8")
                        parts.append({
                            "inline_data": {
                                "mime_type": img.content_type,
                                "data": encoded
                            }
                        })
           
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                res_data = r.json()
                if "candidates" in res_data:
                    return {"data": res_data["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            print(f"Error Gemini: {e}")

    # Respaldo OpenAI
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error: {str(e)}"}

    return {"data": "System busy."}

# --- PAGOS ---
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    base_url = "https://smartcargo-aipa.onrender.com"
    success_url = f"{base_url}/?access=granted&awb={awb}"

    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}

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
            success_url=success_url,
            cancel_url=base_url,
        )
        return {"url": session.url}
    except Exception as e:
        return {"error": str(e)}
