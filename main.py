import os
import stripe
import httpx
import base64
import openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Configuración de Seguridad y CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Carga de Credenciales desde Render
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home():
    # Sirve el HTML principal
    return FileResponse("index.html")

@app.get("/app.js")
async def serve_js():
    # Sirve la lógica de frontend
    return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    # Instrucción Maestra del Asesor Técnico
    system_instruction = (
        "You are the Technical Advisory Engine of SmartCargo by May Roga LLC. "
        "Your mission is to audit cargo and documents to mitigate risks (IATA, DOT, TSA, Maritime). "
        "If images are missing or not clear, ask specific technical questions (weight, HAZMAT class, pallet type). "
        "Provide immediate operational solutions. Be technical, brief, and professional. "
        f"Always respond in: {lang}."
    )

    # Preparación de contenido para motores de visión
    parts = [{"text": f"{system_instruction}\n\n{prompt}"}]

    if GEMINI_KEY:
        # MECÁNICA DE CASCADA (6 INTENTOS): Probamos rutas y modelos hasta que uno responda
        models = [
            "v1beta/models/gemini-1.5-flash",
            "v1/models/gemini-1.5-flash",
            "v1/models/gemini-1.5-flash-latest",
            "v1beta/models/gemini-1.5-flash-8b",
            "v1beta/models/gemini-1.5-pro",
            "v1/models/gemini-1.5-pro"
        ]
        
        # Procesar hasta 3 imágenes si el cliente las envió
        if files:
            for img in files[:3]:
                content = await img.read()
                if content:
                    parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(content).decode("utf-8")
                        }
                    })

        async with httpx.AsyncClient() as client:
            for model_path in models:
                url = f"https://generativelanguage.googleapis.com/{model_path}:generateContent?key={GEMINI_KEY}"
                try:
                    r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                    res_data = r.json()
                    
                    if "candidates" in res_data:
                        # Éxito: Retornamos respuesta del primer motor que funcione
                        return {"data": res_data["candidates"][0]["content"]["parts"][0]["text"]}
                    else:
                        # Error de ruta: Registramos en logs sin mostrar la API KEY
                        print(f"Intento fallido con {model_path}: {res_data.get('error', {}).get('message')}")
                        continue 
                except Exception as e:
                    print(f"Error de conexión con {model_path}")
                    continue

    # RESPALDO TOTAL: Si Google falla en sus 6 intentos, entra OpenAI (GPT-4o)
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction}, 
                    {"role": "user", "content": prompt}
                ]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            print(f"Fallo crítico en motor de respaldo OpenAI: {e}")

    return {"data": "System busy. Our advisors are currently verifying the data manually. Please try again in 2 minutes."}

@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...), 
    awb: str = Form(...), 
    user: Optional[str] = Form(None), 
    password: Optional[str] = Form(None)
):
    base_url = "https://smartcargo-aipa.onrender.com" 
    success_url = f"{base_url}/?access=granted&awb={awb}"

    # ACCESO ADMINISTRATIVO (Gratis para ti)
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}

    # PASARELA DE COBRO STRIPE
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"SmartCargo Audit Ref: {awb}"},
                    "unit_amount": int(amount * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=base_url,
        )
        return {"url": session.url}
    except Exception as e:
        return {"error": str(e)}
