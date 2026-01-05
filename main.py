import os
import stripe
import httpx
import base64
import openai
import io
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from dotenv import load_dotenv
from PIL import Image, ImageOps

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- CONFIGURACIÓN ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home():
    return FileResponse("index.html", media_type="text/html")

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js", media_type="application/javascript")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    # PROMPT DE AUDITOR-ASESOR DE SMARTCARGO
    instruction = (
        f"You are the Senior Technical Advisor for SMARTCARGO by MAY ROGA LLC. Respond in {lang}. "
        "LEGAL POSITION: You are a PRIVATE ADVISOR, not a government official (TSA, IATA, DOT, Customs). "
        "MANDATE: Analyze cargo with the rigor of an official auditor to detect non-compliance, then provide legitimate solutions to pass inspections. "
        "STRICT RULE: Never suggest illegal acts. If a document like an AirWaybill (AWB) is wrong, the only solution is to stop and call the issuer, broker, or owner to fix it at the source. "
        "THREE-LEVEL SOLUTIONS: For physical issues, always provide: "
        "1. ECONOMIC (Quick/Low cost), 2. MEDIUM (Industry standard), 3. PRO/PREMIUM (High end/Full certification). "
        "FORMAT: [AUDIT FINDING] (What an inspector will see), [RISK] (Why it will be held), [TACTICAL SOLUTIONS] (The 3 levels: Economic, Medium, Pro)."
    )

    parts = [{"text": f"{instruction}\n\nCargo Issue: {prompt}"}]

    if GEMINI_KEY:
        try:
            if files:
                for img in files[:3]:
                    content = await img.read()
                    if content:
                        encoded = base64.b64encode(content).decode("utf-8")
                        parts.append({
                            "inline_data": {
                                "mime_type": img.content_type,
                                "data": encoded
                            }
                        })
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                res_data = r.json()
                if "candidates" in res_data:
                    return {"data": res_data["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            print(f"Error Gemini: {e}")

    return JSONResponse({"data": "Service temporarily busy. Please try again."}, status_code=500)

@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    base_url = "https://smartcargo-aipa.onrender.com"
    success_url = f"{base_url}/?access=granted&awb={awb}"

    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"SmartCargo Advisory AWB: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=base_url,
        )
        return {"url": session.url}
    except Exception as e:
        return {"error": str(e)}
