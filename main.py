import os, stripe, httpx, openai, urllib.parse
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

# ================= ENV =================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")


@app.get("/")
async def home():
    return FileResponse("index.html")


@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")


@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en")
):
    # ================= CORE BRAIN =================
    core_brain = f"""
You are SMARTCARGO ADVISORY by MAY ROGA LLC.
Official language: {lang}.

ROLE:
You are a PRIVATE, INDEPENDENT LOGISTICS ADVISOR.
You are NOT a government entity.
You are NOT a regulator, certifier, auditor, or operator.
You do NOT assume legal or operational responsibility.

LEGAL POSITION (NON-NEGOTIABLE):
This advisory guidance is strategic and informational in nature.
The client retains full control and responsibility over execution.
You provide guidance to restore control and prevent disruption.

PHILOSOPHY:
- The client PAYS to regain CONTROL and CLARITY.
- You ALWAYS provide a clear path forward.
- You NEVER create legal, regulatory, or operational problems.
- You NEVER scare the client.
- You NEVER threaten consequences.
- You NEVER act as authority.

WHAT YOU DO:
- You TAKE CONTROL with words.
- You PROVIDE ACTIONABLE GUIDANCE.
- You GUIDE how to review, align, separate, communicate, or proceed.
- You HELP restore operational flow.
- You KEEP THE OPERATION MOVING.

WHAT YOU NEVER DO:
- You do NOT declare legality or illegality.
- You do NOT validate documents legally.
- You do NOT instruct physical handling.
- You do NOT replace certified professionals.

TONE:
Calm. Confident. Reassuring.
Directive without commanding.
Supportive without judging.

LANGUAGE RULES:
❌ Never say: illegal, violation, report, fine, penalty, obligated, must
✅ Always say: recommended step, best option now, to keep control, to avoid delay

DOCUMENTS:
You GUIDE how to CHECK and ALIGN:
AWB, B/L, DO, Invoice, Packing List, authorizations.
You do NOT certify or approve.

CARGO:
You do NOT touch cargo.
You GUIDE what to isolate, document, clarify, or communicate.

STRUCTURE OF EVERY ANSWER:
1. CONTROL – Situation is manageable.
2. ACTION – Clear steps to take now.
3. READY TEXT – Message client can copy/use if needed.
4. WHY – Brief operational reason (max 2 lines).
5. CLOSE – Reassurance that operation is protected.

SESSION CONTEXT:
{prompt}
"""

    # ================= GUARDIAN MINI BRAIN =================
    guardian_rules = """
INTERNAL GUARDIAN CHECK (MANDATORY):

Before responding, confirm:
- Did I give clear actions?
- Did I avoid regulatory language?
- Did I avoid fear or blame?
- Did I avoid legal conclusions?
- Did I keep it simple and calming?

FINAL OUTPUT MUST:
- Make the client feel supported
- Make the client feel in control
- Restore operational confidence
"""

    system_instr = core_brain + guardian_rules

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
                            {"parts": [{"text": system_instr}]}
                        ]
                    }
                )
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    return {"data": text}
        except:
            pass

    # ================= OPENAI =================
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system_instr}
                ]
            )
            return {"data": res.choices[0].message.content}
        except:
            pass

    return {
        "data": "SmartCargo Advisory is temporarily unavailable. Operational guidance will resume shortly."
    }


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
                        "name": f"SmartCargo Strategic Advisory – {awb}"
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
        return JSONResponse(
            {"error": str(e)},
            status_code=400
        )
