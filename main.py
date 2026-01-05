import os, stripe, httpx, openai
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- CONFIGURACIÓN DE LLAVES ---
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

# --- MOTOR DE ASESORÍA (CEREBRO LOGÍSTICO) ---
@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es")):
    # INSTRUCCIÓN: REVISAR, CHEQUEAR, RECTIFICAR, ASESORAR
    instruction = (
        f"Eres el Senior Master Advisor de SmartCargo (May Roga LLC). Responde en {lang}. "
        "PROHIBIDO usar la palabra 'auditar'. Tu función es REVISAR, CHEQUEAR, RECTIFICAR y ASESORAR. "
        "CONOCIMIENTO: IATA, TSA, DOT, Marítimo, Aduanas. "
        "ESTRATEGIA: "
        "1. Inicia con: 'Claro que sí, vamos a revisar y chequear esto juntos para que todo esté correcto'. "
        "2. Guía paso a paso: 'Primero, chequeemos el campo [X]. ¿Qué información ves ahí? Vamos a rectificar si coincide'. "
        "3. No des listas largas; pregunta por un dato a la vez para acompañar al cliente. "
        "4. Usa [🔴 ADVERTENCIA TÉCNICA] para puntos críticos. "
        "FINALIZA: '--- SmartCargo Advisory chequeó su carga hoy. Siempre a su lado para asesorarle. ---'"
    )

    try:
        # Intento 1: Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": [{"text": f"{instruction}\n\nConsulta: {prompt}"}]}]}, timeout=35.0)
            return {"data": r.json()['candidates'][0]['content']['parts'][0]['text']}
    except:
        # Intento 2: OpenAI (Redundancia)
        if OPENAI_KEY:
            try:
                client_oa = openai.OpenAI(api_key=OPENAI_KEY)
                res = client_oa.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
                )
                return {"data": res.choices[0].message.content}
            except: pass
    
    return {"data": "Cerebro técnico en espera. Por favor, reintente en unos segundos."}

# --- SISTEMA DE PAGOS Y ACCESO ADMIN ---
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...), 
    awb: str = Form(...), 
    user: Optional[str] = Form(None), 
    password: Optional[str] = Form(None)
):
    # Bypass para Administrador
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={awb}&tier={amount}"}
    
    try:
        # Creación de sesión de Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Asesoría Técnica SmartCargo - Ref: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost:8000')}/?access=granted&awb={awb}&tier={amount}",
            cancel_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost:8000')}/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
