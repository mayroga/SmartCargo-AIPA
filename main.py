import os, stripe, httpx, openai, urllib.parse, base64
from fastapi import FastAPI, Form, Request
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
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory(prompt: str = Form(""), image_data: str = Form(""), lang: str = Form("auto")):
    # INSTRUCCIÓN BLINDADA: Sin mención a tecnología ni auditoría
    instruction = (
        f"Eres el Senior Master Advisor de SmartCargo (MAY ROGA LLC). Idioma: {lang}. "
        "Experto en IATA, DOT, TSA, CBP (Aduanas USA) y logística global. "
        "Analiza datos visuales y ofrece soluciones técnicas directas para prevenir multas. "
        "PROHIBIDO: No menciones que eres un sistema digital, ni uses la palabra 'auditoría'. "
        "Eres un asesor experto consultado por el cliente. "
        "Finaliza: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    parts = []
    if "," in image_data:
        header, data = image_data.split(",", 1)
        mime = header.split(";")[0].replace("data:", "")
        parts.append({"inline_data": {"mime_type": mime, "data": data.replace(" ", "+").strip()}})
    
    parts.append({"text": f"{instruction}\n\nConsulta del cliente: {prompt}"})

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient(timeout=35.0) as client:
            r = await client.post(url, json={"contents": [{"parts": parts}]})
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"data": text}
    except:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "user", "content": [{"type": "text", "text": instruction + "\n" + prompt}]}]
            )
            return {"data": res.choices[0].message.content}
    return {"data": "Servicio temporalmente no disponible."}

@app.post("/create-payment")
async def pay(amount: float = Form(...), awb: str = Form(...), user: str = Form(None), password: str = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": "./?access=granted"}
    try:
        domain = os.getenv("DOMAIN_URL", "https://smartcargo-aipa.onrender.com")
        s = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{domain}/?access=granted",
            cancel_url=f"{domain}/"
        )
        return {"url": s.url}
    except Exception as e: return JSONResponse({"error": str(e)}, status_code=400)
