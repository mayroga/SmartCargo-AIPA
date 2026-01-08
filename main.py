import os
import stripe
import httpx
import openai
import urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Configuración de CORS para acceso total desde la web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Variables de Entorno (Asegúrate de tenerlas en tu servidor)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es")):
    # INSTRUCCIONES MAESTRAS DE SMARTCARGO ADVISORY BY MAY ROGA LLC
    system_instr = (
        f"Eres el Cerebro Estratégico Quirúrgico de SmartCargo by MAY ROGA LLC. Idioma: {lang}. "
        "IDENTIDAD: Asesoría Privada de alto nivel. No eres IATA, DOT, TSA ni CBP. Eres el experto que conoce sus reglas mejor que nadie. "
        "FILOSOFÍA DE RESPUESTA: Tienes el conocimiento infinito para mitigar retenciones, retornos y ahorrar dinero. "
        "LENGUAJE LEGAL Y SEGURO: Siempre usa lenguaje de sugerencia y propuesta (ej. 'Le sugiero...', 'Mi recomendación estratégica es...', 'Propongo proceder de esta forma...'). "
        "REGLA DE ORO: PROHIBIDO dar clases, definiciones de libro o pasos genéricos de 'búsqueda'. "
        "TÚ TOMAS EL MANDO: Si el cliente pregunta por un Bill of Lading o AWB, no le digas que lo busque, dile: "
        "'Le sugiero mirar el campo X; si no ve el sello Y, mi recomendación es no autorizar la salida para evitar multas'. "
        "PROHIBIDO: Jamás remitas al cliente a otro experto o asesor. TÚ eres el único experto por el que pagó. "
        "CERO TEORÍA: Si el cliente está perdido, guíalo con preguntas de asociación: '¿Huele a gas?', '¿Hay etiquetas de diamante?'. "
        "ACCIÓN: Antes, Durante y Después de cada situación logística. Resuelve AHORA."
        f"\n\nContexto de la Sesión Actual: {prompt}"
    )

    # IA DUAL: PLAN A (Gemini 1.5 Flash para velocidad y búsqueda en nube)
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": system_instr}]}]})
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    return {"data": text}
        except Exception:
            pass

    # IA DUAL: PLAN B (OpenAI GPT-4o para precisión extrema y respaldo)
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_instr}],
                temperature=0.1
            )
            return {"data": res.choices[0].message.content}
        except Exception:
            pass

    return {"data": "Sugerencia del Sistema: El enlace de inteligencia no está disponible temporalmente. Recomendamos contactar a soporte de MAY ROGA LLC."}

@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...), 
    awb: str = Form(...), 
    user: Optional[str] = Form(None), 
    password: Optional[str] = Form(None)
):
    # Acceso Maestro para el Administrador
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    
    # Procesamiento de Pago mediante Stripe
    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Asesoría Estratégica SmartCargo: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/",
        )
        return {"url": checkout.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    # Puerto dinámico para Render/Heroku o local
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
