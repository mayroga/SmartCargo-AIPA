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

# --- CONSTITUCIÓN TÉCNICA SMARTCARGO ---
TECH_CORE = """
Eres el Cerebro Estratégico de SMARTCARGO ADVISORY by MAY ROGA LLC.
NORMATIVA: IATA DGR, TSA, CBP, GOM AVIANCA.

REGLA DE MEDIDAS: Formato dual siempre: [Pulgadas] INC / [Centímetros] CM.
VOZ Y LECTURA: Escribe de forma limpia. NO uses asteriscos (*), almohadillas (#) ni guiones bajos (_). 
ESTILO: Resumen ejecutivo proactivo. Si falta info, interroga. Si hay riesgo, advierte primero.
"""

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), role: Optional[str] = Form("auto")):
    system_instr = f"{TECH_CORE}\nIdioma: {lang}. Rol: {role}. Situación: {prompt}"
    async with httpx.AsyncClient(timeout=55.0) as client:
        # FRENTE 1: GEMINI
        try:
            res_g = await client.post(
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                json={"contents": [{"parts": [{"text": system_instr}]}]}
            )
            if res_g.status_code == 200:
                return {"data": res_g.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass
        # FRENTE 2: OPENAI
        if OPENAI_KEY:
            try:
                res_o = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                    json={"model": "gpt-4o", "messages": [{"role": "system", "content": system_instr}], "temperature": 0.2}
                )
                if res_o.status_code == 200:
                    return {"data": res_o.json()["choices"][0]["message"]["content"]}
            except: pass
    return {"data": "SISTEMA SATURADO. REINTENTE EN 10 SEGUNDOS."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), p: Optional[str] = Form(None)):
    if user == os.getenv("ADMIN_USERNAME") and p == os.getenv("ADMIN_PASSWORD"):
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f'Asesoría AWB: {awb}'}, 'unit_amount': int(amount * 100)}, 'quantity': 1}],
            mode='payment',
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/",
        )
        return {"url": session.url}
    except Exception as e: return JSONResponse({"error": str(e)}, status_code=400)
