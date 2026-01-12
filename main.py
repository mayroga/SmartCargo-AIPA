import os, stripe, httpx, urllib.parse, openai
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

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
        "ACCIÓN: Antes, Durante y Después de cada situación logística. Resuelve AHORA. "
        "NOTA DE VOZ: No uses asteriscos ni símbolos raros para que la lectura de voz sea fluida."
        f"\n\nContexto de la Sesión Actual: {prompt}"
    )

    # IA DUAL: PLAN A (Gemini 1.5 Flash)
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": system_instr}]}]})
                if r.status_code == 200:
                    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return {"data": text}
        except Exception: pass

    # IA DUAL: PLAN B (OpenAI GPT-4o)
    if OPENAI_KEY:
        try:
            # Usamos httpx para OpenAI para evitar bloqueos de sincronía en Render
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                    json={
                        "model": "gpt-4o",
                        "messages": [{"role": "system", "content": system_instr}],
                        "temperature": 0.1
                    }
                )
                if res.status_code == 200:
                    return {"data": res.json()["choices"][0]["message"]["content"]}
        except Exception: pass

    return {"data": "Sugerencia del Sistema: El enlace de inteligencia no está disponible temporalmente. Recomendamos contactar a soporte de MAY ROGA LLC."}

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
    except Exception as e: return JSONResponse({"error": str(e)}, status_code=400)
