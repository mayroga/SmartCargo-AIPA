from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="SmartCargo-AIPA")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ENV ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "disabled")

# ---------------- LEGAL CORE ----------------
LEGAL_TEXT = {
    "Spanish": (
        "🔴 AVISO LEGAL – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA opera exclusivamente como plataforma de ASESORÍA PREVENTIVA.\n"
        "No sustituimos decisiones de aerolíneas, agentes de carga, autoridades aeroportuarias, "
        "TSA, CBP, DOT ni ninguna entidad gubernamental.\n\n"
        "La información proporcionada tiene como único objetivo reducir rechazos, demoras, "
        "multas y pérdidas económicas mediante orientación anticipada.\n\n"
        "La responsabilidad final sobre la carga, documentación y cumplimiento normativo "
        "recae exclusivamente en el usuario.\n"
    ),
    "English": (
        "🔴 LEGAL NOTICE – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA operates strictly as a PREVENTIVE ADVISORY platform.\n"
        "We do not replace decisions made by airlines, cargo agents, airport authorities, "
        "TSA, CBP, DOT or any governmental entity.\n\n"
        "The information provided is intended solely to reduce rejections, delays, fines "
        "and financial losses through early guidance.\n\n"
        "Final responsibility for cargo, documentation and regulatory compliance "
        "remains exclusively with the user.\n"
    )
}

# ---------------- GEMINI ----------------
def run_gemini(prompt: str):
    if not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-pro",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("Gemini failed:", e)
        return None

# ---------------- OPENAI ----------------
def run_openai(prompt: str):
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("OpenAI failed:", e)
        return None

# ---------------- SEMAFORO ----------------
def semaforo(text: str):
    t = text.lower()
    if any(w in t for w in ["reject", "forbidden", "prohibited", "not allowed"]):
        return "RED"
    if any(w in t for w in ["review", "verify", "conditional", "warning"]):
        return "YELLOW"
    return "GREEN"

# ---------------- FRONT ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return open("frontend/index.html", encoding="utf-8").read()

# ---------------- VALIDATE ----------------
@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...)
):
    prompt = f"""
You are SMARTCARGO-AIPA, acting as an experienced cargo advisory assistant.
Analyze the following cargo documentation and explain in simple, clear language.

Classify the result strictly as:
GREEN – acceptable
YELLOW – conditional
RED – not acceptable

Documentation:
{dossier}
"""

    analysis = run_gemini(prompt) or run_openai(prompt)

    if not analysis:
        analysis = (
            "System advisory notice: Unable to process the document at this time. "
            "Please review documentation manually or try again later."
        )

    return JSONResponse({
        "status": semaforo(analysis),
        "analysis": analysis,
        "disclaimer": LEGAL_TEXT.get(lang, LEGAL_TEXT["English"])
    })

# ---------------- ADMIN ----------------
@app.post("/admin")
def admin(
    username: str = Form(...),
    password: str = Form(...),
    question: str = Form(...)
):
    if password != ADMIN_PASSWORD:
        return JSONResponse({"answer": "Unauthorized"}, status_code=401)

    answer = run_openai(question) or "AI unavailable"
    return {"answer": answer}
