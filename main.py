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
# CORE ADVISORY ENGINE
# =========================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    image_data: Optional[str] = Form(None)
):
    instruction = (
        f"You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Language: {lang}. "
        "You are a Tactical Logistics General. Provide EXECUTIVE SOLUTIONS only.\n\n"

        "STRUCTURE:\n"
        "1. DIRECT DIAGNOSIS\n"
        "2. WHERE TO LOOK\n"
        "3. THREE ACTIONABLE SOLUTIONS\n\n"

        "RULES:\n"
        "- Be direct. No theory.\n"
        "- If image provided, analyze FIRST.\n"
        "- We are PRIVATE. NOT GOVERNMENT.\n\n"
        "--- SmartCargo Advisory by MAY ROGA LLC ---"
    )

    result = {
        "data": "SYSTEM: No data received. Please describe your cargo or document.",
        "image": image_data
    }

    # =========================
    # PLAN A — GEMINI
    # =========================
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        )

        parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]

        if image_data and "," in image_data:
            b64_clean = image_data.split(",")[1].replace(" ", "+").strip()
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": b64_clean
                }
            })

        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(url, json={
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "maxOutputTokens": 600,
                    "temperature": 0.1
                }
            })

        j = r.json()
        if "candidates" in j and j["candidates"]:
            result["data"] = j["candidates"][0]["content"]["parts"][0]["text"]
            return result

    except Exception as e:
        print("Gemini Error:", e)

    # =========================
    # PLAN B — OPENAI BACKUP
    # =========================
    try:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)

            content = [{"type": "text", "text": instruction + "\n" + prompt}]
            if image_data:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_data}
                })

            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content}],
                max_tokens=600
            )

            result["data"] = res.choices[0].message.content
            return result

    except Exception as e:
        result["data"] = f"TECH ERROR: {str(e)}"

    return result

# =========================
# STRIPE PAYMENT
# =========================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # MASTER ACCESS
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {
            "url": f"./?access=granted&awb={urllib.parse.quote(awb)}&monto=0"
        }

    try:
        domain = os.getenv(
            "DOMAIN_URL",
            "https://smartcargo-aipa.onrender.com"
        )

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
            success_url=(
                f"{domain}/?access=granted"
                f"&awb={urllib.parse.quote(awb)}"
                f"&monto={amount}"
            ),
            cancel_url=f"{domain}/",
        )

        return {"url": checkout.url}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

# =========================
# VISION MICRO-SERVICE
# =========================
@app.post("/vision-scan")
async def vision_scan(
    image_data: str = Form(...),
    lang: str = Form("en")
):
    """
    Pure vision engine.
    Uses OpenAI only.
    Protected by frontend access flow.
    """
    try:
        client_oa = openai.OpenAI(api_key=OPENAI_KEY)

        prompt = (
            "Perform a strict visual inspection.\n"
            "If document: list visible fields, numbers, dates, signatures.\n"
            "If cargo: identify labels, UN numbers, damages, markings.\n"
            "Be objective. No assumptions."
        )

        res = client_oa.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data}
                    }
                ]
            }],
            max_tokens=400
        )

        return {
            "description": res.choices[0].message.content
        }

    except Exception as e:
        return {"error": str(e)}
