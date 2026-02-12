# main.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

# ---------------- APP CONFIG ----------------
app = FastAPI(title="SmartCargo-AIPA")

# Crear carpeta 'static' si no existe
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ENVIRONMENT VARIABLES ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

# ---------------- GEMINI ENGINE (PRIMARY) ----------------
try:
    from google import genai
except ImportError:
    genai = None

def run_gemini(prompt: str):
    if not GEMINI_API_KEY or not genai:
        return None
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        models = client.models.list()
        selected_model = next((m.name for m in models if "generateContent" in getattr(m, "supported_actions", [])), None)
        if not selected_model:
            return None

        response = client.models.generate_content(model=selected_model, contents=prompt)
        full_text = []
        if hasattr(response, "candidates"):
            for c in response.candidates:
                if hasattr(c, "content") and hasattr(c.content, "parts"):
                    for p in c.content.parts:
                        if hasattr(p, "text"):
                            full_text.append(p.text)
        return "\n".join(full_text).strip() or None
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

# ---------------- OPENAI ENGINE (BACKUP) ----------------
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
        print(f"OpenAI error: {e}")
        return None

# ---------------- CLASSIFICATION LOGIC ----------------
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
        return "<h1>SmartCargo-AIPA Frontend Not Found</h1>"

# ---------------- VALIDATE CARGO ----------------
@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form("English"),
    dossier: str = Form(...)
):
    prompt = f"""
    Act as the Senior Advisor of SmartCargo-AIPA by May Roga.
    You are a high-level specialist in IATA, DOT, CBP, and airline compliance.

    GOLDEN RULES:
    - Do NOT mention you are an AI.
    - Use "Advisory", "Review", "Rectification".
    - Respond professional, technical, direct.
    - ALWAYS use Markdown TABLES.

    ANALYSIS:
    1. Review this cargo/documentation: {dossier}
    2. Classify as: GREEN, YELLOW, RED.
    3. Generate TABLE: [Reviewed Point | Finding | Suggested Action].
    4. Up to 3 preventive recommendations.
    5. End with 2 key closure questions.

    Response language: {lang}
    """

    analysis = run_gemini(prompt) or run_openai(prompt)
    if not analysis:
        analysis = "Notice: Advisory system temporarily unavailable. Please perform a manual review."

    return JSONResponse({
        "status": semaforo(analysis),
        "analysis": analysis,
        "disclaimer": LEGAL_TEXT.get(lang, LEGAL_TEXT["English"])
    })

# ---------------- ADMIN ASK SIN LOGIN ----------------
@app.post("/admin")
def admin(question: str = Form(...)):
    # Ya no pide username/password
    answer = run_openai(question) or run_gemini(question) or "Service unavailable"
    return {"answer": answer}
