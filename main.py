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

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), image_data: Optional[str] = Form(None)):
    # EL CEREBRO MAESTRO (Millones de casos: IATA, TSA, CBP, DOT)
    instruction = (
        f"Role: Senior Master Advisor SmartCargo (MAY ROGA LLC). Language: {lang}. "
        "Knowledge: Global Logistics Expert (IATA, DOT, TSA, Maritime, US Customs). "
        "Action: Provide bold, technical solutions for millions of hazardous and logistics scenarios. "
        "Prohibited: NEVER use the word 'audit'. Be a direct advisor. "
        "Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    try:
        # PROTOCOLO DE PRE-CARGA Y ANÁLISIS DUAL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        clean_data = image_data.split(",")[1].replace(" ", "+") if image_data else None
        
        parts = [{"text": f"{instruction}\n{prompt}"}]
        if clean_data:
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": clean_data}})

        async with httpx.AsyncClient(timeout=35.0) as client:
            r = await client.post(url, json={"contents": [{"parts": parts}]})
            return {"data": r.json()['candidates'][0]['content']['parts'][0]['text']}
    except:
        if OPENAI_KEY: # Respaldo Dual
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            content = [{"type": "text", "text": instruction + "\n" + prompt}]
            if image_data: content.append({"type": "image_url", "image_url": {"url": image_data}})
            res = client_oa.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": content}])
            return {"data": res.choices[0].message.content}
    return {"data": "Acceso denegado o error de sistema."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    # Entrada por Clave Maestra
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}"}
    # Entrada por Pago
    try:
        domain = os.getenv('DOMAIN_URL', 'https://smartcargo-aipa.onrender.com')
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{domain}/",
        )
        return {"url": session.url}
    except Exception as e: return JSONResponse({"error": str(e)}, status_code=400)
