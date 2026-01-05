import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- LLAVES Y CREDENCIALES ---
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
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en")):
    instruction = (
        "You are the Senior Master Advisor of SmartCargo (May Roga LLC). "
        "MISSION: REVIEW, CHECK, RECTIFY, ADVISE. No 'audits'. "
        "Detect language and respond in the SAME language. Use global knowledge (IATA, TSA, DOT, IMDG). "
        "Ask for specific technical data (UN#, Dimensions, Weights, HS Codes) immediately. "
        "Finalize: '--- SmartCargo Advisory checked your cargo today. Always by your side. ---'"
    )

    # INTENTO 1: GEMINI (Filtro de 6 segundos)
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": [{"text": f"{instruction}\n\nUser: {prompt}"}]}]}, timeout=6.0)
            res_data = r.json()
            if 'candidates' in res_data and res_data['candidates']:
                return {"data": res_data['candidates'][0]['content']['parts'][0]['text']}
            else: raise Exception("Invalid Format")
    except:
        # INTENTO 2: OPENAI (Respaldo si Gemini falla o tarda)
        if OPENAI_KEY:
            try:
                client_oa = openai.OpenAI(api_key=OPENAI_KEY)
                res = client_oa.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}],
                    timeout=12.0
                )
                return {"data": res.choices[0].message.content}
            except: return {"data": "Cerebro técnico saturado. Reintente."}
    
    return {"data": "System busy. Try again."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    clean_awb = urllib.parse.quote(awb)
    
    # --- ACCESO PARA TI (ADMIN BYPASS) ---
    if user and password:
        if user == ADMIN_USER and password == ADMIN_PASS:
            return {"url": f"/?access=granted&awb={clean_awb}&tier={amount}"}
    
    # --- COBRO STRIPE ---
    domain = os.getenv("DOMAIN_URL", "https://smartcargo-aipa.onrender.com")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={clean_awb}&tier={amount}",
            cancel_url=f"{domain}/",
        )
        return {"url": session.url}
    except Exception as e: return JSONResponse({"error": str(e)}, status_code=400)
