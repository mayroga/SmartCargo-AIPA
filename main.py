import os, stripe, httpx, urllib.parse
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# --- CONSTITUCIÓN TÉCNICA SMARTCARGO ADVISORY BY MAY ROGA LLC ---
TECH_CORE = """
Eres el Cerebro Estratégico Quirúrgico de SmartCargo by MAY ROGA LLC. 
IDENTIDAD: Asesoría Privada de alto nivel. No eres IATA, DOT, TSA ni CBP; eres el experto que domina sus reglas.
FILOSOFÍA: Tu objetivo es mitigar retenciones, retornos y ahorrar capital al Shipper y Forwarder.

REGLAS DE ORO:
1. FORMATO DUAL: Cada dimensión o límite de tamaño debe mostrarse en: [Pulgadas] INC / [Centímetros] CM.
2. LENGUAJE EXPERTO: Usa lenguaje de sugerencia estratégica (ej. 'Mi recomendación es...', 'Propongo proceder...').
3. TOMA EL MANDO: No des definiciones de libro. Si falta info, interroga. Si hay riesgo, advierte.
4. HILO CONDUCTOR: Mantén el contexto de la conversación hasta la resolución del problema.
5. VOZ LIMPIA: No uses asteriscos (*) ni símbolos para que la bocina lea el texto de forma fluida.
"""

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...), 
    lang: str = Form("es"), 
    role: Optional[str] = Form("auto")
):
    """Motor de IA: OpenAI (Principal) -> Gemini (Respaldo)"""
    system_instr = f"{TECH_CORE}\nIdioma: {lang}. Rol: {role}. Situación: {prompt}"
    
    async with httpx.AsyncClient(timeout=50.0) as client:
        # PLAN A: OPENAI GPT-4o (PRIORIDAD 1)
        if OPENAI_KEY:
            try:
                res_o = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": [{"role": "system", "content": system_instr}],
                        "temperature": 0.2
                    }
                )
                if res_o.status_code == 200:
                    return {"data": res_o.json()["choices"][0]["message"]["content"]}
            except Exception as e:
                print(f"Error OpenAI: {e}")

        # PLAN B: GEMINI 1.5 FLASH (RESPALDO / PRIORIDAD 2)
        if GEMINI_KEY:
            try:
                url_g = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                res_g = await client.post(
                    url_g, 
                    json={"contents": [{"parts": [{"text": system_instr}]}]},
                    headers={"Content-Type": "application/json"}
                )
                if res_g.status_code == 200:
                    return {"data": res_g.json()["candidates"][0]["content"]["parts"][0]["text"]}
            except Exception as e:
                print(f"Error Gemini: {e}")

    return {"data": "SMARTCARGO ADVISORY: Error de conexión con los cerebros de IA. Verifique API Keys en Render."}

@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...), 
    awb: str = Form(...), 
    user: Optional[str] = Form(None), 
    p: Optional[str] = Form(None)
):
    if user == os.getenv("ADMIN_USERNAME") and p == os.getenv("ADMIN_PASSWORD"):
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Asesoría Estratégica SmartCargo - AWB: {awb}',
                    },
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
