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
NORMATIVA: IATA DGR, TSA 1544, 49 CFR DOT, CBP, GOM AVIANCA.

REGLA DE MEDIDAS OBLIGATORIA:
Cada vez que menciones una dimensión, medida o límite de tamaño, 
DEBES mostrarla en formato dual al final de la frase o en el resumen: 
Ejemplo: "La altura máxima para Bellies es 63 INC / 160 CM".
Usa siempre Pulgadas (INC) y Centímetros (CM).

FILOSOFÍA: 
1. RESOLUCIÓN: Si el cliente pregunta algo vago, interrógale con autoridad técnica (¿Es PAX o CAO?, ¿Tiene sello HT ISPM-15?, ¿Presentó Original 2 y 4?).
2. ASESORÍA ACTIVA: No des conceptos. Enseña a hacer la papelería, muestra ejemplos de embalaje y guía paso a paso.
3. ACCIÓN: Pasos directos: "Mueva la etiqueta", "Firme en rojo", "Saque el manifiesto".
4. BLINDAJE: Evita multas y rechazos en counter de Avianca mediante educación preventiva.
"""

# --- RUTAS DE SERVICIO (CORREGIDAS) ---

@app.get("/")
async def home():
    # ESTO ASEGURA QUE SE VEA LA APP Y NO EL CÓDIGO
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), role: Optional[str] = Form("auto")):
    system_instr = f"{TECH_CORE}\nIdioma: {lang}. Rol: {role}. Situación: {prompt}"
    async with httpx.AsyncClient(timeout=55.0) as client:
        try:
            res_g = await client.post(
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                json={"contents": [{"parts": [{"text": system_instr}]}]}
            )
            if res_g.status_code == 200:
                return {"data": res_g.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass
        if OPENAI_KEY:
            try:
                res_o = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                    json={"model": "gpt-4o", "messages": [{"role": "system", "content": system_instr}], "temperature": 0}
                )
                if res_o.status_code == 200:
                    return {"data": res_o.json()["choices"][0]["message"]["content"]}
            except: pass
    return {"data": "SISTEMA SATURADO. REINTENTE."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), p: Optional[str] = Form(None)):
    if user == os.getenv("ADMIN_USERNAME") and p == os.getenv("ADMIN_PASSWORD"):
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
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
