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

# =========================
# INIT
# =========================
load_dotenv()
app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# ENV VARS
# =========================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL", "https://smartcargo-aipa.onrender.com")

# =========================
# STATIC FILES
# =========================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

# =========================
# HELPER: Parse AI Response
# =========================
def parse_ai_response(response_json):
    text = ""
    if "candidates" in response_json:  # Gemini
        for c in response_json["candidates"]:
            if "content" in c:
                parts = c["content"].get("parts", [])
                for p in parts:
                    if "text" in p:
                        text += p["text"] + "\n"
    elif "choices" in response_json:  # OpenAI
        try:
            text += response_json["choices"][0]["message"]["content"]
        except:
            pass
    return text.strip()

# =========================
# ADVISORY ENGINE
# =========================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    image_data: Optional[str] = Form(None)  # Solo referencia visual
):
    instruction = f"""
You are SmartCargo Advisory by MAY ROGA LLC.
Language: {lang}.
Roles: Shipper, Forwarder, Operator, Trucker, Manager.
Objective: Solve any logistics problem IMMEDIATELY, BEFORE, DURING, and AFTER operations.
Do NOT say "I don't know", "call someone", or give theory.
Focus only on ACTIONABLE, DIRECT, STEP-BY-STEP SOLUTIONS.
Client input: {prompt}
"""
    result = {"data": "SYSTEM: No data received."}

    # -------------------------
    # PLAN A - GEMINI
    # -------------------------
    try:
        if GEMINI_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            parts = [{"text": instruction}]
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(url, json={
                    "contents": [{"parts": parts}],
                    "generationConfig": {"maxOutputTokens": 800, "temperature": 0.1}
                })
                result_text = parse_ai_response(r.json())
                if result_text:
                    result["data"] = result_text
                    return result
    except Exception as e:
        print("Gemini Error:", e)

    # -------------------------
    # PLAN B - OPENAI BACKUP
    # -------------------------
    try:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": instruction}],
                max_tokens=800
            )
            result_text = parse_ai_response(res.to_dict())
            if result_text:
                result["data"] = result_text
    except Exception as e:
        result["data"] = f"TECH ERROR: {str(e)}"

    return result

# =========================
# STRIPE / MASTER PAYMENT
# =========================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # -------------------------
    # MASTER ACCESS
    # -------------------------
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"./?access=granted&awb={urllib.parse.quote(awb)}&monto=0"}

    # -------------------------
    # STRIPE PAYMENT
    # -------------------------
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
