from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

# OCR
import pytesseract
from PIL import Image
import io

# Gemini (Google)
try:
    from google import genai
except ImportError:
    genai = None

app = FastAPI(title="SmartCargo-AIPA")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ENV ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "disabled")

# ---------------- LEGAL + BANNER ----------------
LEGAL_TEXT = {
    "Spanish": (
        "🔴 AVISO LEGAL – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA opera únicamente como plataforma de ASESORÍA PREVENTIVA.\n"
        "No sustituimos decisiones de aerolíneas, agentes de carga, TSA, CBP, DOT u "
        "autoridades gubernamentales.\n"
        "La responsabilidad final sobre la carga y cumplimiento normativo es del usuario.\n"
        "Si se utiliza OCR para analizar documentos, el usuario asume toda la responsabilidad sobre resultados automatizados.\n\n"
        "💙 BENEFICIOS: Evita rechazos, delays, multas, ahorra tiempo, esfuerzo y dinero."
    ),
    "English": (
        "🔴 LEGAL NOTICE – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA operates strictly as a PREVENTIVE ADVISORY platform.\n"
        "We do not replace decisions made by airlines, cargo agents, TSA, CBP, DOT or "
        "government authorities.\n"
        "Final responsibility for cargo and regulatory compliance remains with the user.\n"
        "If OCR is used to analyze documents, the user assumes full responsibility for automated results.\n\n"
        "💙 BENEFITS: Avoid rejections, delays, fines, save time, effort and money."
    )
}

# ---------------- GEMINI ----------------
def run_gemini(prompt: str):
    if not GEMINI_API_KEY or not genai:
        return None
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-pro",
            contents=prompt
        )
        return getattr(response, "text", None)
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
    if any(w in t for w in ["reject", "rejection", "forbidden", "prohibited", "not allowed", "must be rejected"]):
        return "RED"
    if any(w in t for w in ["conditional", "review", "verify", "correct", "re-label", "fix", "warning"]):
        return "YELLOW"
    return "GREEN"

# ---------------- OCR ----------------
def run_ocr(file_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print("OCR failed:", e)
        return ""

def apply_ocr_rules(ocr_text: str):
    """Reglas hard OCR para seguridad y cumplimiento"""
    ocr_text_lower = ocr_text.lower()
    # HAWB / AWB inconsistentes
    if "hawb" in ocr_text_lower and "awb" in ocr_text_lower:
        if "inconsistent" in ocr_text_lower or "diferente" in ocr_text_lower:
            return "RED", "AWB/HAWB inconsistente detectado por OCR"
    # Dry Ice / Lithium hard rules
    if "dry ice" in ocr_text_lower or "lithium" in ocr_text_lower:
        return "RED", "Carga peligrosa (Dry Ice / Lithium) detectada → acción inmediata requerida"
    return None, None

# ---------------- FRONT ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return open("frontend/index.html", encoding="utf-8").read()

# ---------------- VALIDATE ----------------
@app.post("/validate")
async def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...),
    use_ocr: bool = Form(False),
    ocr_file: UploadFile = None,
    airline: str = Form("Avianca")
):
    # ---------------- OCR OPCIONAL ----------------
    ocr_status, ocr_message = None, None
    if use_ocr and ocr_file:
        file_bytes = await ocr_file.read()
        ocr_text = run_ocr(file_bytes)
        ocr_status, ocr_message = apply_ocr_rules(ocr_text)

    prompt = f"""
You are SMARTCARGO-AIPA, acting as a SENIOR AIR CARGO COUNTER SUPERVISOR
with deep operational knowledge of {airline} Cargo, IATA DGR, TSA and CBP rules.

Your task is to PREVENT rejections, delays and fines BEFORE cargo acceptance.

Analyze the cargo documentation below exactly as a real counter agent would.

MANDATORY OUTPUT STRUCTURE:
1. OVERALL STATUS (🟢 GREEN / 🟡 YELLOW / 🔴 RED)
2. DETAILED FINDINGS (Counter-Level)
3. RISK LEVEL
4. REQUIRED COUNTER ACTIONS
5. FINAL DECISION

STRICT RULES:
- Do NOT be vague
- DRY ICE or LITHIUM → RED automatic
- Hidden labels / handwriting illegible / document inconsistencies → not GREEN
- OCR inconsistencies must be reported if used
- Responsibility final → Avianca, TSA, CBP, Government; May Roga LLC solo asesora

Cargo documentation:
{dossier}
"""

    analysis = run_gemini(prompt) or run_openai(prompt)

    if ocr_status == "RED":
        analysis = f"{analysis}\n\n🚨 OCR ALERT: {ocr_message}\nStatus escalated to RED automatically."

    if not analysis:
        analysis = (
            "System advisory notice: Unable to process the document at this time. "
            "Please review documentation manually."
        )

    return JSONResponse({
        "status": ocr_status or semaforo(analysis),
        "analysis": analysis,
        "disclaimer": LEGAL_TEXT.get(lang, LEGAL_TEXT["English"])
    })

# ---------------- ADMIN ----------------
@app.post("/admin")
async def admin(
    username: str = Form(...),
    password: str = Form(...),
    question: str = Form(...)
):
    if password != ADMIN_PASSWORD:
        return JSONResponse({"answer": "Unauthorized"}, status_code=401)

    answer = run_openai(question) or "AI unavailable"
    return {"answer": answer}
