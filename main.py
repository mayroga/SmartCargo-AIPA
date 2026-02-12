# main.py
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ---------------- APP CONFIG ----------------
app = FastAPI(title="SmartCargo-AIPA")

# Montar carpeta de archivos estáticos
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ENV VARIABLES ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SmartCargo2026")

# ---------------- LEGAL & COMPLIANCE ----------------
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

# ---------------- GEMINI ENGINE ----------------
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
        selected_model = next(
            (m.name for m in models if "generateContent" in getattr(m, "supported_actions", [])), 
            None
        )
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

# ---------------- OPENAI ENGINE ----------------
def run_openai(prompt: str):
    if not OPENAI_API_KEY:
        return None
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

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
        return "<h1>SmartCargo-AIPA Frontend Not Found</h1>"

@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form("English"),
    dossier: str = Form(...)
):
    # Lógica de cascada y filtro letal
    prompt = f"""
    Act as the Senior Advisor of SmartCargo-AIPA by May Roga. 
    You are a high-level specialist in IATA, DOT, CBP, and airline compliance.

    🔹 FOLLOW CASCADING LOGIC:
    - Only show relevant questions depending on cargo type.
    - If 'Perishable', skip Lithium Battery questions and go to Temperature.
    - If 'DG', only show DGD, UN labels, and skip Perishable block.
    - Apply lethal filters: Belly PAX >80cm = BLOCK, Missing DGD = NO RECEIVE, etc.

    🔹 GENERATE:
    1. Table with columns: Reviewed Point | Finding | Suggested Action
    2. Semáforo: GREEN / YELLOW / RED
    3. Up to 3 preventive recommendations
    4. Final solution: whom to contact or action to take

    DOCUMENTATION TO REVIEW:
    {dossier}

    Language: {lang}
    """
    analysis = run_gemini(prompt) or run_openai(prompt)
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
    if password != ADMIN_PASSWORD:
        return JSONResponse({"answer": "Access Denied"}, status_code=401)

    answer = run_openai(question) or run_gemini(question) or "Service unavailable"
    return {"answer": answer}
