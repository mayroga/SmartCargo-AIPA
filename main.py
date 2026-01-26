import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# ======================================================
# IA IMPORTS (SAFE)
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
# ENV VARIABLES
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
# FRONTEND
# ======================================================

@app.get("/", response_class=HTMLResponse)
def home():
    return FRONTEND.read_text(encoding="utf-8")

# ======================================================
# IA CORE (GEMINI → OPENAI FALLBACK)
# ======================================================

def run_ai(prompt: str) -> str:

    # ---------- GEMINI 1.5 ----------
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print("Gemini failed:", e)

    # ---------- OPENAI ----------
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

    return "AI unavailable. Please contact system administrator."

# ======================================================
# VALIDATE CARGO
# ======================================================

@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...)
):
    prompt = f"""
You are SMARTCARGO-AIPA, acting as a SENIOR AVIanca Cargo MIA counter agent.

Analyze EXACTLY as a real cargo counter would.

You MUST:
- Detect documentary errors
- Detect TSA violations
- Detect CBP issues
- Detect DOT and IATA compliance issues
- Evaluate shipper, driver, warehouse responsibility

STRICT DECISION RULES:
GREEN  = Fully acceptable
YELLOW = Conditional / Correctable
RED    = Reject – Not acceptable

Explain clearly.
Educate the client.
Be professional and precise.
Language: {lang}

DOCUMENTATION PROVIDED:
{dossier}
"""

    analysis = run_ai(prompt)

    status = "GREEN"
    analysis_upper = analysis.upper()

    if "REJECT" in analysis_upper or "NOT ACCEPTABLE" in analysis_upper:
        status = "RED"
    elif "WARNING" in analysis_upper or "CONDITIONAL" in analysis_upper:
        status = "YELLOW"

    return JSONResponse({
        "status": status,
        "analysis": analysis,
        "disclaimer": (
            "SMARTCARGO-AIPA is a preventive advisory system. "
            "Final authority belongs to Avianca Cargo, TSA and CBP."
        )
    })

# ======================================================
# ADMIN CORE
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

Answer with full authority using:
- Avianca Cargo procedures
- IATA regulations
- TSA / CBP / DOT compliance
- Real operational counter logic

QUESTION:
{question}
"""

    answer = run_ai(prompt)
    return {"answer": answer}
