import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js(): return FileResponse("app.js")

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    base_url = "https://smartcargo-aipa.onrender.com" 
    success_url = f"{base_url}/?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS: return {"url": success_url}
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory AWB: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=base_url
    )
    return {"url": session.url}

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(""), lang: str = Form("en"), files: List[UploadFile] = File(None)):
    instruction = (
        "You are the Senior Technical Expert of SmartCargo by May Roga LLC. "
        "Your goal is to provide IMMEDIATE, PRACTICAL SOLUTIONS to cargo problems. "
        "Do not use filler words. Go straight to the point based on millions of logistics scenarios. "
        "If you see a risk (DOT, IATA, IMDG), give the exact corrective action to save the shipment. "
        f"Respond in: {lang}."
    )
    parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
    if files:
        for img in files[:3]:
            content = await img.read()
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(content).decode("utf-8")}})

    async with httpx.AsyncClient() as client:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        try:
            r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
            return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}])
            return {"data": res.choices[0].message.content}
