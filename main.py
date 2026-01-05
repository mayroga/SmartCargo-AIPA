import os, stripe, httpx, openai
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es")):
    # INSTRUCCIÓN MAESTRA: CONOCIMIENTO GLOBAL INFINITO
    instruction = (
        "Eres el Senior Master Advisor de SmartCargo (May Roga LLC). "
        "TU BASE DE DATOS ES GLOBAL: Tienes acceso a millones de escenarios de logística, leyes IATA, TSA, DOT, IMDG, y regulaciones aduaneras de todos los países. "
        "REGLA DE ORO: No te limites a los ejemplos del usuario. Usa tu inteligencia para predecir riesgos que el usuario ni siquiera imagina. "
        "COMPORTAMIENTO: Si el usuario te da un dato, REVISA y CHEQUEA contra toda la normativa internacional. "
        "Si pregunta por algo general, pide inmediatamente los datos críticos (Dimensiones, UN#, Peso, HS Code, Incoterm). "
        "LENGUAJE: Responde SIEMPRE en el idioma en que el usuario te escribe. Detecta el idioma automáticamente. "
        "PROHIBIDO: Usar 'auditar'. Usa REVISAR, CHEQUEAR, RECTIFICAR, ASESORAR. "
        "ESTRUCTURA: [🔴 ALERTA TÉCNICA], Solución Guerrilla, Solución Industrial, Solución Elite. "
        "FINALIZA: '--- SmartCargo Advisory chequeó su carga hoy. Siempre a su lado para asesorarle. ---'"
    )

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": [{"text": f"{instruction}\n\nConsulta del Cliente: {prompt}"}]}]}, timeout=35.0)
            return {"data": r.json()['candidates'][0]['content']['parts'][0]['text']}
    except:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
    return {"data": "Cerebro técnico saturado. Reintente."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={awb}&tier={amount}"}
    
    # URL Dinámica para Render
    domain = os.getenv("DOMAIN_URL", "https://smartcargo-aipa.onrender.com")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"SmartCargo Advisory: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={awb}&tier={amount}",
            cancel_url=f"{domain}/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
