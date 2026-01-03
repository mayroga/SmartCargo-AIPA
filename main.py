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

# Carga de Credenciales
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    # Instrucción Maestra de May Roga LLC
    system_instruction = (
        "Eres el Motor de Asesoría Técnica de SmartCargo por May Roga LLC. "
        "Tu misión es auditar visualmente la carga y documentos para mitigar riesgos (IATA, DOT, TSA). "
        "Si las imágenes no son claras o fallan, inicia un interrogatorio técnico directo. "
        "Proporciona soluciones operativas inmediatas. No menciones que eres una IA. "
        f"Responde siempre en idioma: {lang}."
    )

    # Preparación de partes para visión
    parts = [{"text": f"{system_instruction}\n\n{prompt}"}]

    if GEMINI_KEY:
        try:
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
            
            # MECÁNICA DE CASCADA REFORZADA (6 INTENTOS)
            gemini_urls = [
                # 1. Flash v1beta (La que intentamos primero)
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                # 2. Flash v1 estable
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                # 3. Flash Latest (Ruta de respaldo)
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}",
                # 4. Flash 8B (La versión optimizada, suele funcionar cuando las otras fallan)
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key={GEMINI_KEY}",
                # 5. Gemini 1.5 PRO (El motor más potente, por si Flash está bloqueado)
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}",
                # 6. Gemini 1.5 PRO Estable
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}"
            ]
            
            async with httpx.AsyncClient() as client:
                for url in gemini_urls:
                    try:
                        r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                        res_data = r.json()
                        
                        if "candidates" in res_data:
                            # Éxito: Retornamos el análisis de Gemini
                            return {"data": res_data["candidates"][0]["content"]["parts"][0]["text"]}
                        else:
                            print(f"Ruta fallida ({url}): {res_data.get('error', {}).get('message')}")
                    except Exception as e:
                        print(f"Error de conexión en ruta {url}: {e}")
                        continue
        except Exception as e:
            print(f"Fallo general en motor Gemini: {e}")

    # RESPALDO FINAL: Si todo lo anterior falla, entra OpenAI (Solo Texto)
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}]
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

    # Acceso Administrativo Directo
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}

    # Pasarela de Stripe para Clientes
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"SmartCargo Advisory Ref: {awb}"},
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
