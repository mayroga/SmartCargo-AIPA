import os, stripe, httpx, base64
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "SmartAdmin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "Ley")

@app.post("/cargas")
async def quick_audit(h: float = Form(...), ispm: str = Form(...), dg: str = Form(...)):
    res = []
    if h > 213: res.append({"msg": "Over TSA Height Limit", "sol": "1. Re-pack below 213cm (Fastest). 2. Request physical screening (Slowest).", "lvl": "high"})
    if ispm == "NO": res.append({"msg": "No Wood Stamp", "sol": "1. Swap to Plastic Pallet. 2. Get certified HT treatment.", "lvl": "high"})
    return res

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), images: List[UploadFile] = File(None)):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    instruction = (
        f"You are SMARTCARGO CONSULTING. Respond in {lang}. "
        "Provide multiple legal solutions for the cargo to move. "
        "ORDER: 1. FASTEST & CHEAPEST Solution. 2. INTERMEDIATE Solution. 3. STRUCTURAL (Expensive) Solution. "
        "Never mention AI. Be professional and offer stability."
    )

    parts = [{"text": f"{instruction}\n\nClient Request: {prompt}"}]
    if images:
        for img in images[:3]:
            img_data = await img.read()
            if img_data: parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(img_data).decode("utf-8")}})

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=55.0)
        try:
            return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except:
            return {"data": "Consultant is busy. Please try again."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS: return {"url": success_url}
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}

@app.get("/")
async def serve_home(): return FileResponse("index.html") if os.path.exists("index.html") else HTMLResponse("404", status_code=404)
app.mount("/", StaticFiles(directory=".", html=True), name="static")
