import os
import stripe
import httpx
import openai
import urllib.parse
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
DOMAIN_URL = os.getenv("DOMAIN_URL")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en")):
    system_instr = (
        f"You are the Lead Strategic Logistics Advisor at MAY ROGA LLC. Language: {lang}. "
        "The client has paid for a solution. If the input is empty or 'Not specified', YOU MUST TAKE CONTROL. "
        "Ask the client what they see, tell them where to look (manifests, stickers, truck door), and explain the common risks for their Role. "
        "Your mission is to resolve the problem (Before, During, After) using your infinite knowledge of DOT, CBP, TSA, IATA, and Maritime law. "
        "Be surgical, direct, and summaries. Do not give lessons, give ACTIONABLE STEPS."
        f"Data: {prompt}"
    )

    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": system_instr}]}]})
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if text: return {"data": text}
        except: pass

    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_instr}],
                temperature=0.1
            )
            return {"data": res.choices[0].message.content}
        except: pass

    return {"data": "System offline. Contact MAY ROGA LLC."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}
    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Expert Advisory: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/",
        )
        return {"url": checkout.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
