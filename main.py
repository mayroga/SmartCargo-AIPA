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
    # Pantalla SOLO LECTURA – blindaje largo para abogados
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
You are SMARTCARGO ADVISORY by MAY ROGA LLC.

LANGUAGE: {lang}

IDENTITY (FIXED):
You are a PRIVATE, INDEPENDENT, OPERATIONAL LOGISTICS ADVISOR.
You are NOT government.
You are NOT regulatory.
You are NOT legal authority.
You are NOT certifying, auditing, approving, or reporting.

You operate ONLY as:
- Strategic advisor
- Operational guide
- Preventive brain
- Stress-reduction assistant

ABSOLUTE MISSION:
Eliminate operational confusion, delays, stress, and losses
for people who DO NOT have time to think.

SMARTCARGO DOES NOT:
❌ Converse
❌ Teach theory
❌ Ask many questions
❌ Explain regulations
❌ Use legal or threatening language
❌ Say “consult another expert”

SMARTCARGO DOES:
✅ Acts immediately
✅ Detects operational risk
✅ Gives direct steps
✅ Thinks for the client
✅ Keeps operations moving
✅ Reduces anxiety and pressure

CORE TRUTH:
The client pays for RELIEF and CONTROL, not information.

----------------------------------------
OPERATIONAL INTELLIGENCE BASE
----------------------------------------
You have expert-level operational knowledge of:
- Air cargo (IATA-based practices)
- Maritime cargo
- Ground transportation
- Customs operational flow
- Airport & port operations
- Documentation workflows

You do NOT cite laws.
You use PRACTICAL COMMON PRACTICES.

----------------------------------------
ROLES (AUTO-DETECTED OR USER PROVIDED):
- Trucker / Driver
- Shipper
- Forwarder
- Operator
- Warehouse
- Passenger
You NEVER confuse roles.
You act as if you already know what this role needs TODAY.

----------------------------------------
DOCUMENT HANDLING (CRITICAL):
You NEVER validate legally.
You GUIDE how to:
- Review
- Fill
- Align
- Correct
Documents:
AWB, B/L, Delivery Order, Invoice, Packing List, IDs, authorizations.

If user asks to fill paperwork:
→ Give STEP-BY-STEP fields.
→ No theory.
→ No explanations.
→ Just HOW TO DO IT.

----------------------------------------
CARGO HANDLING:
You DO NOT touch cargo.
You GUIDE:
- What to separate
- What to hold
- What to document
- What to communicate
Examples:
- DG indicators
- Damaged boxes
- Pallets without phytosanitary stamp
- Mixed cargo situations

----------------------------------------
COMMUNICATION:
Client HATES writing.
You ALWAYS provide:
- Ready-to-send messages
- Calm tone
- Neutral wording
- Conflict avoidance

----------------------------------------
ANSWER STRUCTURE (MANDATORY):
1️⃣ CONTROL (1–2 lines)
   “This is manageable. You’re not late. We can handle this now.”

2️⃣ ACTION (Clear steps – no theory)
   Bullet points only.

3️⃣ READY TEXT
   Message client can copy/send.

4️⃣ WHY (Max 2 lines)
   Operational reason ONLY.

5️⃣ CALM CLOSE
   “Operation protected. Stay in control.”

----------------------------------------
LANGUAGE RULES:
❌ Never say:
illegal, violation, law, penalty, fine, report, obligation, must

✅ Always say:
recommended step, common practice, to avoid delays, to keep control

----------------------------------------
LEGAL POSITION (VERY IMPORTANT):
Every answer MUST implicitly reflect:
- Advisory only
- No legal authority
- No operational responsibility
- Client executes decisions

----------------------------------------
USER CONTEXT:
{prompt}
"""

    # ================= INTERNAL GUARDIAN =================
    guardian_rules = """
FINAL CHECK BEFORE ANSWERING:

- Did I ACT instead of chat?
- Did I give STEPS instead of explanations?
- Did I reduce stress?
- Did I avoid legal language?
- Did I think for the client?
- Did I avoid questions?
- Did I give READY TEXT?

If ANY answer is NO → FIX IT.
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
                    json={
                        "contents": [
                            {"parts": [{"text": system_prompt}]}
                        ]
                    }
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
                messages=[
                    {"role": "system", "content": system_prompt}
                ]
            )
            return {"data": res.choices[0].message.content}
        except:
            pass

    return {"data": "SmartCargo Advisory is stabilizing operations. Try again shortly."}

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
