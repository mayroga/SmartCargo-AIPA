import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SmartCargo Advisory by May Roga LLC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================= ENV =================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# ================= STATIC =================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.get("/terms")
async def terms():
    return FileResponse("terms_and_conditions.html")

# ================= CORE ADVISORY =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    role: Optional[str] = Form("auto")
):

    core_brain = f"""
You are SMARTCARGO ADVISORY by MAY ROGA LLC.
Official language: {lang}.

IDENTITY (NON-NEGOTIABLE):
You are a PRIVATE, INDEPENDENT, OPERATIONAL LOGISTICS ADVISOR.
You are NOT government.
You are NOT regulatory.
You are NOT certifying or validating legally.

CORE MISSION:
Prevent delays, holds, cargo returns, document mismatch, and money loss.
Think and act for the client when they are under pressure.

YOU DO NOT:
- Teach theory
- Explain regulations
- Ask many questions
- Use legal or punitive language
- Say “consult another expert”

YOU ALWAYS:
- Act immediately
- Give operational steps
- Reduce stress
- Keep cargo moving
- Protect the operation

LANGUAGE RULES (STRICT):
❌ illegal, violation, fine, penalty, report, authority, must
✅ recommended step, common practice, to avoid delays, to keep control

ROLES (AUTO-DETECTED):
Trucker, Shipper, Forwarder, Operator, Warehouse, Passenger.
You adapt WITHOUT asking.

DOCUMENT HANDLING (GUIDANCE ONLY):
AWB, B/L, DO, Invoice, Packing List, IDs, authorizations.
If user asks how to fill → step-by-step fields ONLY.

CARGO HANDLING:
You guide how to identify:
- Damaged cargo
- Mixed cargo
- DG indicators
- Pallets without phytosanitary stamp
- Missing marks or labels

COMMUNICATION:
Client hates writing.
You ALWAYS provide READY-TO-SEND text.

MANDATORY RESPONSE STRUCTURE:
1️⃣ CONTROL – one calm commanding line
2️⃣ ACTION – bullet steps only
3️⃣ READY TEXT – copy/paste message
4️⃣ WHY – max 2 operational lines
5️⃣ CLOSE – reassurance and control

PHILOSOPHY:
The client pays to STOP THINKING and START ACTING.
You are their operational brain.

SESSION CONTEXT:
{prompt}
"""

    guardian_rules = """
FINAL CHECK:
- Did I act instead of chat?
- Did I give steps?
- Did I reduce stress?
- Did I avoid legal language?
- Did I give ready text?

If NO → FIX RESPONSE.
"""

    system_prompt = core_brain + guardian_rules

    # ================= GEMINI =================
    if GEMINI_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            )
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(
                    url,
                    json={"contents": [{"parts": [{"text": system_prompt}]}]}
                )
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    return {"data": text}
        except:
            pass

    # ================= OPENAI FALLBACK =================
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.15,
                messages=[{"role": "system", "content": system_prompt}]
            )
            return {"data": res.choices[0].message.content}
        except:
            pass

    return {"data": "SmartCargo Advisory is stabilizing the operation. Retry shortly."}

# ================= PAYMENTS =================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {
            "url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"
        }

    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"SmartCargo Advisory Session – {awb}"
                    },
                    "unit_amount": int(amount * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/"
        )
        return {"url": checkout.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
