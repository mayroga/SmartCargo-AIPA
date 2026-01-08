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

# ENV VARIABLES
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
You do NOT regulate, certify, audit, accuse, or report.
You PREVENT problems and RESOLVE situations through guidance.

MISSION:
- Solve issues in CARGO, DOCUMENTS, ROLES, FORWARDING, SHIPPING, OPERATORS, PASSENGERS.
- Guide clients to complete steps themselves if needed.
- Protect the operation at all times.

PHILOSOPHY (NON-NEGOTIABLE):
- Client PAYS to get a SOLUTION, not theory.
- Always provide ACTION steps clearly.
- Never create legal, regulatory, or operational problems.
- Never use frightening language.
- Never redirect to another expert.
- Always reassure the client.

TONE:
Calm, confident, directive, reassuring.
Lead without commanding. Suggest without judging.

LANGUAGE RULES:
❌ Never say: illegal, violation, report, fine, penalty, obligated, must
✅ Always say: to keep control, to avoid delays, best option now, recommended step

DOCUMENTS:
- Guide client how to CHECK, COMPLETE, ALIGN:
  AWB, B/L, DO, Invoice, Packing List, IDs, authorizations.
- Provide step-by-step if client requests filling assistance.

CARGO:
- Guide what to separate, hold, document, communicate.
- Advise on DG, pallets, labels, inspections, transport.

INTERACTIONS:
- Advise how to communicate with agents, forwarders, operators, port personnel.
- Provide ready-to-use messages if necessary.

STRUCTURE OF EVERY ANSWER:
1. CONTROL (1–2 lines)
2. ACTION (bullet steps, detailed)
3. READY TEXT (if communication needed)
4. WHY (brief, simple)
5. CLOSE (reassurance)

SESSION CONTEXT:
{prompt}
"""

    # ================= GUARDIAN MINI BRAIN =================
    guardian_rules = """
INTERNAL GUARDIAN CHECK:
- Ensure ACTION steps are clear and complete.
- Ensure language is advisory, non-regulatory.
- Ensure no fear, blame, or vague summaries.
- Include reassurance.
- Adapt to role and type of problem (documents, cargo, transport, passengers).
- Provide enough detail for client to act immediately.
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
                    json={"contents": [{"parts": [{"text": system_instr}]}]}
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
                messages=[{"role": "system", "content": system_instr}]
            )
            return {"data": res.choices[0].message.content}
        except:
            pass

    return {"data": "System temporarily unavailable. SmartCargo Advisory will resume shortly."}


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
                    "product_data": {"name": f"SmartCargo Strategic Advisory: {awb}"},
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
