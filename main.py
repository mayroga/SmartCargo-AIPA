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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL", "https://smartcargo-aipa.onrender.com")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

def parse_ai_response(response_json):
    text = ""
    if "candidates" in response_json:
        for c in response_json["candidates"]:
            if "content" in c:
                parts = c["content"].get("parts", [])
                for p in parts:
                    if "text" in p: text += p["text"] + "\n"
    elif "choices" in response_json:
        try: text += response_json["choices"][0]["message"]["content"]
        except: pass
    return text.strip()

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), image_data: Optional[str] = Form(None)):
    instruction = f"You are SmartCargo Advisory by MAY ROGA LLC. Lang: {lang}. Direct, actionable logistics solutions only. Input: {prompt}"
    result = {"data": "SYSTEM: AI Error"}
    
    try:
        if GEMINI_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(url, json={"contents": [{"parts": [{"text": instruction}]}]})
                result["data"] = parse_ai_response(r.json())
                return result
    except Exception as e: print(e)
    return result

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    # MASTER ACCESS CORREGIDO
    if user == ADMIN_USER and password == ADMIN_PASS:
        # Forzamos la redirección absoluta con los parámetros
        success_url = f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}&monto=0"
        return {"url": success_url}

    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Advisory Ref: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}&monto={amount}",
            cancel_url=f"{DOMAIN_URL}/",
        )
        return {"url": checkout.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
