import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# ---------------- IA ----------------
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ---------------- APP ----------------
app = FastAPI(title="SMARTCARGO-AIPA")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
FRONTEND = Path("frontend/index.html")

# ---------------- ENV ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Configura Gemini si está disponible
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Configura OpenAI si está disponible
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ---------------- FRONT ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return FRONTEND.read_text(encoding="utf-8")

# ---------------- IA CORE ----------------
def run_ai(prompt: str) -> str:
    """
    Primero intenta Gemini, si falla o no está disponible usa OpenAI.
    """
    # ---------------- GEMINI ----------------
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            if hasattr(response, "text") and response.text:
                return response.text
        except Exception as e:
            print("Gemini failed:", e)

    # ---------------- OPENAI ----------------
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        try:
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return res.choices[0].message.content
        except Exception as e:
            print("OpenAI failed:", e)

    return "AI unavailable."

# ---------------- VALIDATION ----------------
@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...)
):
    full_text = f"""
CLIENT INPUT:
{dossier}
"""

    prompt = f"""
You are SMARTCARGO-AIPA, senior Avianca Cargo MIA counter.

Analyze exactly as counter would.
Detect documentary, TSA, CBP, DOT, IATA issues.
Decide GREEN / YELLOW / RED.
Explain clearly.
Educate client.
Language: {lang}.

TEXT:
{full_text}
"""

    analysis = run_ai(prompt)

    status = "GREEN"
    if "REJECT" in analysis.upper():
        status = "RED"
    elif "WARNING" in analysis.upper():
        status = "YELLOW"

    return JSONResponse({
        "status": status,
        "analysis": analysis,
        "disclaimer": "SMARTCARGO-AIPA is a preventive advisory system. Final authority belongs to Avianca Cargo, TSA and CBP."
    })

# ---------------- ADMIN ----------------
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
Answer with full Avianca, IATA, TSA, CBP, DOT expertise.

QUESTION:
{question}
"""
    answer = run_ai(prompt)
    return {"answer": answer}
