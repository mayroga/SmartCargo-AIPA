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
    # ================= SMARTCARGO CORE BRAIN =================
    core_brain = f"""
SMARTCARGO ADVISORY by May Roga LLC
Official language: {lang}

IDENTITY (LEGAL DISCLAIMER):
- Provided by May Roga LLC
- Not government, not regulatory, not legally certified
- Advisory only, client executes decisions
- No operational responsibility is assumed by May Roga LLC

MISSION:
- Prevent delays, holds, returns, document mismatch, cargo errors, and money loss
- Think and act for client under operational pressure

YOU DO NOT:
- Certify or validate legally
- Teach theory
- Use legal, punitive, or regulatory language
- Redirect client to another expert (unless explicitly needed)

YOU ALWAYS:
- Give operational guidance
- Provide practical steps
- Protect cargo and documentation flow
- Reduce stress and mental load
- Deliver READY-TO-SEND communications

LANGUAGE RULES:
❌ illegal, violation, fine, penalty, report, authority, must
✅ recommended step, common practice, to avoid delays, to keep control

ROLES HANDLED:
Trucker, Shipper, Forwarder, Operator, Warehouse, Passenger
- Adapt advice automatically to the role
- Provide steps for each role without asking

DOCUMENTS HANDLED (GUIDANCE):
AWB, B/L, DO, Invoice, Packing List, IDs, authorizations
- If user asks how to fill: step-by-step guidance only

CARGO HANDLING:
- Damaged cargo
- Mixed cargo
- DG indicators
- Pallets without stamps
- Missing marks or labels

COMMUNICATION:
- Client hates writing
- Always provide ready-to-send messages

MANDATORY RESPONSE STRUCTURE:
1️⃣ CONTROL – one calm, commanding line
2️⃣ ACTION – step-by-step operational bullet points
3️⃣ READY TEXT – copy/paste message
4️⃣ WHY – max 2 lines operational reasoning
5️⃣ CLOSE – reassurance, forward motion

LEGAL NOTE IN EVERY ANSWER:
- Advisory only
- No certification or legal validation
- Client responsible for decisions

SESSION CONTEXT:
{prompt}
"""

    # ================= INTERNAL GUARDIAN =================
    guardian_rules = """
FINAL CHECK BEFORE RESPONDING:
- Did I act immediately?
- Did I provide step-by-step guidance?
- Did I reduce stress?
- Did I avoid legal language?
- Did I provide ready-to-send text?

If any answer is NO → fix response.
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
                    return {"data": f"SMARTCARGO ADVISORY by May Roga LLC\n\n{text}"}
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
            return {"data": f"SMARTCARGO ADVISORY by May Roga LLC\n\n{res.choices[0].message.content}"}
        except:
            pass

    return {"data": "SMARTCARGO ADVISORY by May Roga LLC\nSmartCargo Advisory is stabilizing the operation. Retry shortly."}

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
