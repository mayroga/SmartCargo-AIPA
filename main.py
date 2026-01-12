import os, stripe, httpx, urllib.parse
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Configuración de API Keys desde Render
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# --- CONSTITUCIÓN TÉCNICA SMARTCARGO ---
TECH_CORE = """
Eres el Cerebro Estratégico de SMARTCARGO ADVISORY by MAY ROGA LLC.
NORMATIVA: IATA DGR, TSA 1544, 49 CFR DOT, CBP, GOM AVIANCA.

FILOSOFÍA: 
1. RESOLUCIÓN: Si el cliente pregunta algo vago, interrógale (¿Es PAX o CAO?, ¿Sello ISPM-15?, ¿Original 2 y 4?).
2. ACCIÓN: No des conceptos. Da pasos. "Mueva la etiqueta", "Firme en rojo", "Saque el papel del sobre".
3. BLINDAJE: Tu objetivo es que la carga fluya y evitar multas al Shipper y rechazos en el Counter.
"""

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), role: Optional[str] = Form("auto")):
    system_instr = f"{TECH_CORE}\nIdioma: {lang}. Rol: {role}. Situación: {prompt}"
    
    async with httpx.AsyncClient(timeout=55.0) as client:
        # FRENTE 1: GEMINI 1.5 FLASH (Velocidad y Visión)
        try:
            res_g = await client.post(
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                json={"contents": [{"parts": [{"text": system_instr}]}]}
            )
            if res_g.status_code == 200:
                return {"data": res_g.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except:
            pass

        # FRENTE 2 / VALIDADOR MAESTRO: OPENAI GPT-4o (Precisión Técnica)
        if OPENAI_KEY:
            try:
                res_o = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                    json={"model": "gpt-4o", "messages": [{"role": "system", "content": system_instr}], "temperature": 0}
                )
                if res_o.status_code == 200:
                    return {"data": res_o.json()["choices"][0]["message"]["content"]}
            except:
                pass

    return {"data": "SISTEMA SATURADO. REINTENTE EN 5 SEGUNDOS."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: str = Form(None), p: str = Form(None)):
    # Master Login
    if user == os.getenv("ADMIN_USERNAME") and p == os.getenv("ADMIN_PASSWORD"):
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    
    # Pago Real Stripe
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f'Advisory AWB: {awb}'}, 'unit_amount': int(amount * 100)}, 'quantity': 1}],
            mode='payment',
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js(): return FileResponse("app.js")
