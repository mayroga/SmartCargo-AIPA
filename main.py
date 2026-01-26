import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# ======================================================
# SAFE IA IMPORTS
# ======================================================

GEMINI_AVAILABLE = False
OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    pass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    pass

# ======================================================
# APP
# ======================================================

app = FastAPI(title="SMARTCARGO-AIPA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
FRONTEND = Path("frontend/index.html")

# ======================================================
# ENV
# ======================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# ======================================================
# IA CONFIG
# ======================================================

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

openai_client = None
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ======================================================
# FRONT
# ======================================================

@app.get("/", response_class=HTMLResponse)
def home():
    return FRONTEND.read_text(encoding="utf-8")

# ======================================================
# IA CORE (AUTO GEMINI → OPENAI)
# ======================================================

def run_ai(prompt: str) -> str:

    # ---------- GEMINI (AUTO MODEL) ----------
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel()  # ← SIN FORZAR NOMBRE
            response = model.generate_content(prompt)
            if response and hasattr(response, "text") and response.text:
                return response.text
        except Exception as e:
            print("Gemini failed:", e)

    # ---------- OPENAI FALLBACK ----------
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            print("OpenAI failed:", e)

    return "System temporarily unavailable. Please try again later."

# ======================================================
# VALIDATE
# ======================================================

@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...)
):
    prompt = f"""
You are SMARTCARGO-AIPA, acting as a senior Avianca Cargo counter agent in Miami.

Analyze the documentation EXACTLY as a real counter would.

Evaluate:
- Documentary accuracy
- TSA compliance
- CBP requirements
- DOT and IATA regulations
- Operational responsibility (shipper, driver, warehouse)

Decision rules:
GREEN  = Acceptable
YELLOW = Conditional (can be corrected)
RED    = Rejected (not acceptable)

Explain clearly, simply and professionally.
Your explanation must be understandable for any person, not only professionals.
Language: {lang}

DOCUMENTATION:
{dossier}
"""

    analysis = run_ai(prompt)
    text = analysis.upper()

    status = "GREEN"
    if "REJECT" in text or "NOT ACCEPTABLE" in text:
        status = "RED"
    elif "CONDITIONAL" in text or "WARNING" in text:
        status = "YELLOW"

    return {
        "status": status,
        "analysis": analysis,
        "legal_notice": (
            "SMARTCARGO-AIPA is an advisory and preventive system. "
            "Final decisions and legal responsibility remain with Avianca Cargo, "
            "TSA, CBP and applicable authorities."
        )
    }

# ======================================================
# ADMIN
# ======================================================

@app.post("/admin")
def admin(
    username: str = Form(...),
    password: str = Form(...),
    question: str = Form(...)
):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    prompt = f"""
You are SMARTCARGO-AIPA ADMIN CORE.

Provide authoritative answers based on:
- Avianca Cargo procedures
- IATA standards
- TSA, CBP and DOT regulations

QUESTION:
{question}
"""

    answer = run_ai(prompt)
    return {"answer": answer}
