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
async def serve_js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), image_data: Optional[str] = Form(None), lang: str = Form("en")):
    instruction = (
        "You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). PRIVATE TECHNICAL ADVISORS. "
        "Analyze visual evidence: labels, UN codes, and hazards. "
        "Purpose: Prevent fines and holds. No 'audit' words. "
        "EXCELENCIA ESCALADA: Tier $5 (Courier), $15 (Standard), $35 (Critical Shield), $95 (Project Master). "
        "Direct solutions. Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    try:
        # LLAVE: Preparamos las partes (Texto + Imagen si existe)
        parts = [{"text": f"{instruction}\n\nInput: {prompt}"}]
        
        if image_data and "," in image_data:
            # Capturamos la lectura directa (Base64) eliminando el encabezado
            clean_b64 = image_data.split(",")[1].replace(" ", "+").strip()
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": clean_b64
                }
            })

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=15.0)
            res = r.json()
            return {"data": res['candidates'][0]['content']['parts'][0]['text']}
    except Exception as e:
        # Si Gemini falla o no hay imagen, el respaldo de OpenAI sigue funcionando igual
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}])
            return {"data": res.choices[0].message.content}
    return {"data": "System error. Contact Admin."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}&tier={amount}"}
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{os.getenv('DOMAIN_URL')}/?access=granted&awb={urllib.parse.quote(awb)}&tier={amount}",
            cancel_url=f"{os.getenv('DOMAIN_URL')}/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
