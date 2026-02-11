from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

# ---------------- APP ----------------
app = FastAPI(title="SmartCargo-AIPA")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ENV ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "disabled")

# ---------------- LEGAL ----------------
LEGAL_TEXT = {
    "Spanish": (
        "🔴 AVISO LEGAL – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA opera únicamente como plataforma de ASESORÍA PREVENTIVA.\n"
        "No sustituimos decisiones de aerolíneas, agentes de carga, TSA, CBP, DOT u "
        "autoridades gubernamentales.\n"
        "La responsabilidad final sobre la carga y cumplimiento normativo es del usuario.\n\n"
        "💙 BENEFICIOS: Evita rechazos, demoras, multas y pérdidas económicas."
    ),
    "English": (
        "🔴 LEGAL NOTICE – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA operates strictly as a PREVENTIVE ADVISORY platform.\n"
        "We do not replace decisions made by airlines, cargo agents, TSA, CBP, DOT or "
        "government authorities.\n"
        "Final responsibility for cargo and regulatory compliance remains with the user.\n\n"
        "💙 BENEFITS: Avoid rejections, delays, fines and financial loss."
    )
}

# ---------------- GEMINI (FIXED FULL TEXT) ----------------
try:
    from google import genai
except ImportError:
    genai = None


def run_gemini(prompt: str):
    if not GEMINI_API_KEY or not genai:
        return None

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Auto-discover compatible model
        models = client.models.list()
        selected_model = None

        for m in models:
            if "generateContent" in getattr(m, "supported_actions", []):
                selected_model = m.name
                break

        if not selected_model:
            print("Gemini: No compatible model found")
            return None

        response = client.models.generate_content(
            model=selected_model,
            contents=prompt
        )

        # ✅ FIX: reconstruir texto COMPLETO
        full_text = []

        if hasattr(response, "candidates"):
            for c in response.candidates:
                if hasattr(c, "content") and hasattr(c.content, "parts"):
                    for p in c.content.parts:
                        if hasattr(p, "text"):
                            full_text.append(p.text)

        final_text = "\n".join(full_text).strip()
        return final_text if final_text else None

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
    if any(w in t for w in ["reject", "rejected", "forbidden", "prohibited", "not allowed"]):
        return "RED"
    if any(w in t for w in ["review", "verify", "conditional", "warning", "check"]):
        return "YELLOW"
    return "GREEN"


# ---------------- FRONT ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return open("frontend/index.html", encoding="utf-8").read()


# ---------------- VALIDATE (VERSIÓN SMARTCARGO) ----------------
@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...)
):
    # Prompt robusto con identidad SmartCargo y reglas de Avianca
    prompt = f"""
    Actúa como el Asesor Senior de SmartCargo-AIPA. 
    Eres especialista en cumplimiento de IATA, DOT, CBP y normativas de Avianca (Belly/PAX, GSA, COMAT, etc.).
    
    REGLAS ESTRICTAS:
    - NO menciones que eres una IA, inteligencia artificial o modelo de lenguaje.
    - NO uses la palabra "auditoría"; usa "Asesoría", "Revisión" o "Rectificación".
    - Responde de forma concisa pero con mucho peso profesional.
    - Es obligatorio usar TABLAS de Markdown para que la información sea clara.
    
    INSTRUCCIONES:
    1. Analiza esta documentación: {dossier}
    2. Clasifica en: GREEN (Cumple), YELLOW (Requiere atención), RED (Riesgo alto/Rechazo).
    3. Presenta una TABLA con: Punto Revisado, Hallazgo y Acción Sugerida.
    4. Haz exactamente 2 preguntas directas al usuario para resolver el problema rápidamente.
    
    Idioma de respuesta: {lang}
    """

    # Intento con Gemini (Principal) y luego OpenAI (Respaldo)
    analysis = run_gemini(prompt) or run_openai(prompt)

    if not analysis:
        analysis = "Error de conexión. Por favor, realice una revisión manual o intente de nuevo."

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

    answer = run_openai(question) or "AI service unavailable"

    return {"answer": answer}
