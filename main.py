# main.py
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.ai_helper import query_ai

# ---------------- APP CONFIG ----------------
app = FastAPI(title="SmartCargo-AIPA")

# Carpeta de archivos estáticos
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ENVIRONMENT VARIABLES ----------------
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SmartCargo2026")

# ---------------- LEGAL & COMPLIANCE TEXT ----------------
LEGAL_TEXT = {
    "English": (
        "🔴 LEGAL NOTICE – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA operates strictly as a PREVENTIVE ADVISORY platform.\n"
        "We do not replace decisions made by airlines, cargo agents, TSA, CBP, DOT or "
        "government authorities.\n"
        "Final responsibility for cargo and regulatory compliance remains with the user.\n\n"
        "💙 BENEFITS: Avoid rejections, delays, fines and financial loss."
    ),
    "Spanish": (
        "🔴 AVISO LEGAL – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA opera únicamente como plataforma de ASESORÍA PREVENTIVA.\n"
        "No sustituimos decisiones de aerolíneas, agentes de carga, TSA, CBP, DOT u "
        "autoridades gubernamentales.\n"
        "La responsabilidad final sobre la carga y cumplimiento normativo es del usuario.\n\n"
        "💙 BENEFICIOS: Evita rechazos, demoras, multas y pérdidas económicas."
    )
}

# ---------------- SEMÁFORO ----------------
def semaforo(text: str):
    t = text.upper()
    if any(w in t for w in ["RED", "ROJO", "RECHAZO", "REJECT", "FORBIDDEN", "DANGER"]):
        return "RED"
    if any(w in t for w in ["YELLOW", "AMARILLO", "REVISAR", "VERIFICAR", "CHECK", "REVIEW", "VALIDATE"]):
        return "YELLOW"
    return "GREEN"

# ---------------- ENDPOINTS ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    try:
        return open("frontend/index.html", encoding="utf-8").read()
    except FileNotFoundError:
        return "<h1>SMARTCARGO-AIPA Frontend Not Found</h1>"

@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form("English"),
    dossier: str = Form(...)
):
    """
    Valida la carga con todas las 49 preguntas, genera semáforo y recomendaciones.
    """
    prompt = f"""
Act as Senior Advisor of SMARTCARGO-AIPA by May Roga LLC.
You are an expert in IATA, CBP, DOT, FAA, and airline cargo compliance (Freighter, Belly/PAX, COMAT).

RULES:
- Do NOT mention you are AI.
- Always respond in Markdown tables for clarity.
- Analyze the following dossier/documentation: {dossier}
- Evaluate all 49 SMARTCARGO-AIPA questions.
- Assign a semáforo status (GREEN, YELLOW, RED) for each question.
- Provide up to 3 preventive recommendations.
- End with 2 key questions to ensure cargo compliance.

Response language: {lang}
"""

    # Consulta AI (OpenAI o Gemini)
    analysis = query_ai(prompt)
    if not analysis:
        analysis = "Notice: Advisory system temporarily unavailable. Please perform a manual review."

    return JSONResponse({
        "status": semaforo(analysis),
        "analysis": analysis,
        "disclaimer": LEGAL_TEXT.get(lang, LEGAL_TEXT["English"])
    })

@app.post("/admin")
def admin(
    username: str = Form(...),
    password: str = Form(...),
    question: str = Form(...)
):
    """
    Endpoint para el administrador. Solo acceso con password.
    """
    if password != ADMIN_PASSWORD:
        return JSONResponse({"answer": "Access Denied"}, status_code=401)

    answer = query_ai(question) or "Service unavailable"
    return {"answer": answer}
