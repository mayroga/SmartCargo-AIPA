import os, stripe, httpx, base64, io
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def serve_js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), files: List[UploadFile] = File(None)):
    instruction = (
        f"Identify as 'SmartCargo Advisory by May Roga LLC'. Respond in {lang}. "
        "IDENTITY: You are the BRAIN of the logistics chain. Private Technical Advisor. "
        "MISSION: Kill the problem. Save the money. Avoid holds/fines/returns. "
        "UNIVERSAL LOGIC: Apply expert knowledge to ANY logistics scenario (Air, Sea, Land, Docs, Cargo). "
        "METHOD: Analyze step-by-step from top to bottom. If a risk is detected, use: '[🔴 RED LIGHT WARNING]'. "
        "3-LEVEL SOLUTIONS: 1. Economic (Tactical/Fast), 2. Standard (Industry), 3. Pro (Certified). "
        "No trash talk. Be direct. You provide the solution that the hand must execute. "
        "ADVERTISING: End with '--- SmartCargo Advisory protected your cargo today. Recommend us! ---'"
    )

    parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
    if files:
        for f in files[:3]:
            content = await f.read()
            if content:
                parts.append({"inline_data": {"mime_type": f.content_type, "data": base64.b64encode(content).decode("utf-8")}})

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
            return {"data": r.json()['candidates'][0]['content']['parts'][0]['text']}
    except:
        return {"data": "Advisory center offline. Try again."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={awb}&tier={amount}"}
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory Access {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}&tier={amount}",
            cancel_url="https://smartcargo-aipa.onrender.com/"
        )
        return {"url": session.url}
    except: return {"error": "Payment Error"}
