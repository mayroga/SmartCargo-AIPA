import os, stripe, httpx, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv
import openai

load_dotenv()

app = FastAPI(title="SmartCargo Advisory | May Roga LLC")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================= ENV =================
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# ================= STATIC =================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js():
    return FileResponse("app.js")

@app.get("/terms")
async def terms():
    return FileResponse("terms.html")

# ================= CORE ADVISORY =================
@app.post("/advisory")
async def advisory(
    prompt: str = Form(...),
    lang: str = Form("en"),
    role: Optional[str] = Form("auto")
):

    system_prompt = f"""
YOU ARE SMARTCARGO ADVISORY by MAY ROGA LLC.

LANGUAGE: {lang}

IDENTITY:
You are a PRIVATE OPERATIONAL LOGISTICS ADVISOR.
You are NOT legal, NOT regulatory, NOT governmental.
You do NOT certify, approve, validate, report or authorize.

MISSION:
Restore control, reduce stress, keep cargo moving.

YOU NEVER:
- Chat
- Teach theory
- Explain laws
- Ask questions
- Sound academic

YOU ALWAYS:
- Act immediately
- Give steps
- Think for the client
- Prevent delays
- Reduce pressure

DOCUMENTS YOU MASTER:
AWB, B/L, DO, COMMERCIAL INVOICE, PACKING LIST

RULES:
- No legal language
- No fear language
- No long explanations

MANDATORY RESPONSE STRUCTURE:

1. CONTROL
One short calming sentence.

2. ACTION STEPS
Bullets only.

3. DOCUMENT CHECK
Exact fields to verify or align.

4. READY MESSAGE
Copy-paste message.

5. OPERATIONAL WHY
Max 2 lines.

6. CLOSE
Operation protected. Stay in control.

FORBIDDEN WORDS:
illegal, law, fine, penalty, report, obligation, must

APPROVED WORDING:
common practice, recommended step, to avoid delays, to keep control

USER CONTEXT:
{prompt}
"""

    # ========== GEMINI FIRST ==========
    if GEMINI_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                    json={"contents":[{"parts":[{"text": system_prompt}]}]}
                )
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if txt:
                    return {"data": txt}
        except:
            pass

    # ========== OPENAI FALLBACK ==========
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            r = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.15,
                messages=[{"role":"system","content":system_prompt}]
            )
            return {"data": r.choices[0].message.content}
        except:
            pass

    return {"data":"System stabilizing. Retry shortly."}

# ================= PAYMENTS =================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}

    try:
        s = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data":{
                    "currency":"usd",
                    "product_data":{"name":f"SmartCargo Advisory – {awb}"},
                    "unit_amount":int(amount*100)
                },
                "quantity":1
            }],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/"
        )
        return {"url": s.url}
    except Exception as e:
        return JSONResponse({"error":str(e)}, status_code=400)
