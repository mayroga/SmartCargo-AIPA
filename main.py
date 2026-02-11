from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

# ---------------- APP CONFIG ----------------
app = FastAPI(title="SmartCargo-AIPA")

# Asegúrate de que la carpeta 'static' exista para tus CSS/JS
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ENVIRONMENT VARIABLES ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SmartCargo2026") # Cambiar por seguridad

# ---------------- LEGAL & COMPLIANCE TEXT ----------------
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
        
        final_text = "\n".join(full_text).strip()
        return final_text if final_text else None
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

# ---------------- CLASSIFICATION LOGIC (SEMAFORO) ----------------
def semaforo(text: str):
    t = text.upper()
    if any(w in t for w in ["RED", "ROJO", "RECHAZO", "REJECT", "PROHIBIDO", "FORBIDDEN", "DANGER"]):
        return "RED"
    if any(w in t for w in ["YELLOW", "AMARILLO", "REVISAR", "VERIFICAR", "CHECK", "REVIEW", "VALIDAR"]):
        return "YELLOW"
    return "GREEN"

# ---------------- ENDPOINTS ----------------

@app.get("/", response_class=HTMLResponse)
def home():
    # Asegúrate de tener frontend/index.html creado
    try:
        return open("frontend/index.html", encoding="utf-8").read()
    except FileNotFoundError:
        return "<h1>SmartCargo-AIPA Frontend Not Found</h1>"

@app.post("/validate")
def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...)
):
    # Prompt Maestro con Reglas de Identidad y Estructura
    prompt = f"""
    Actúa como el Asesor Senior de SmartCargo-AIPA by May Roga. 
    Eres especialista de alto nivel en cumplimiento de IATA, DOT, CBP y normativas de Avianca (Belly/PAX, Freighter, COMAT).
    
    REGLAS DE ORO:
    - NO menciones que eres una IA, inteligencia artificial o modelo de lenguaje.
    - NO uses la palabra "auditoría"; usa "Asesoría", "Revisión" o "Rectificación".
    - Responde con lenguaje técnico, profesional y directo. Menos palabras, más peso.
    - Es OBLIGATORIO usar TABLAS de Markdown para la claridad.
    
    INSTRUCCIONES DE ANÁLISIS:
    1. Revisa esta carga/documentación: {dossier}
    2. Clasifica estrictamente en: GREEN, YELLOW o RED.
    3. Genera una TABLA con columnas: [Punto Revisado | Hallazgo Encontrado | Acción Sugerida].
    4. Provee máximo 3 recomendaciones preventivas adicionales.
    5. Finaliza con 2 preguntas clave para cerrar la resolución del problema.
    
    Idioma de respuesta: {lang}
    """

    # Ejecución con sistema de respaldo (Fallback)
    analysis = run_gemini(prompt) or run_openai(prompt)

    if not analysis:
        analysis = "Aviso: El sistema de asesoría no está disponible momentáneamente. Realice revisión manual."

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
        return JSONResponse({"answer": "Acceso Denegado"}, status_code=401)

    # El administrador puede hacer consultas técnicas abiertas
    answer = run_openai(question) or run_gemini(question) or "Servicio no disponible"
    return {"answer": answer}

# ---------------- RUN COMMAND ----------------
# Para ejecutar: uvicorn main:app --reload
