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

# ---------------- LEGAL + BANNER ----------------
LEGAL_TEXT = {
    "Spanish": (
        "🔴 AVISO LEGAL – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA opera únicamente como plataforma de ASESORÍA PREVENTIVA.\n"
        "No sustituimos decisiones de aerolíneas, agentes de carga, TSA, CBP, DOT u "
        "autoridades gubernamentales.\n"
        "La responsabilidad final sobre la carga y cumplimiento normativo es del usuario.\n\n"
        "💙 BENEFICIOS: Evita rechazos, delays, multas, ahorra tiempo, esfuerzo y dinero."
    ),
    "English": (
        "🔴 LEGAL NOTICE – SMARTCARGO-AIPA by May Roga LLC\n\n"
        "SmartCargo-AIPA operates strictly as a PREVENTIVE ADVISORY platform.\n"
        "We do not replace decisions made by airlines, cargo agents, TSA, CBP, DOT or "
        "government authorities.\n"
        "Final responsibility for cargo and regulatory compliance remains with the user.\n\n"
        "💙 BENEFITS: Avoid rejections, delays, fines, save time, effort and money."
    )
}

# ---------------- GEMINI ----------------
def run_gemini(prompt: str):
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        if response and response.text:
            return response.text
        return None

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
You are SMARTCARGO-AIPA, acting as a SENIOR AIR CARGO COUNTER SUPERVISOR
with deep operational knowledge of Avianca Cargo, IATA DGR, TSA and CBP rules.

Your task is to PREVENT rejections, delays and fines BEFORE cargo acceptance.

Analyze the cargo documentation below exactly as a real counter agent would.

MANDATORY OUTPUT STRUCTURE:

1. OVERALL STATUS
   - Clearly state ONE of the following:
     🟢 GREEN – ACCEPTABLE
     🟡 YELLOW – CONDITIONAL / CORRECTABLE
     🔴 RED – NOT ACCEPTABLE / REJECT AT COUNTER

2. DETAILED FINDINGS (Counter-Level)
   - List EACH issue separately.
   - For every issue include:
     • What is wrong
     • Why it is a problem (operational / safety / regulatory)
     • Which party is responsible (Shipper, Driver, Agent, Warehouse)

3. RISK LEVEL
   - Explain the real operational risk:
     Delay / Fine / Rejection / Safety violation

4. REQUIRED COUNTER ACTIONS (VERY IMPORTANT)
   - Write EXACT actions a counter agent must take, using imperative language:
     Examples:
     • RE-LABEL OUTSIDE SHRINK WRAP
     • REJECT UNTIL DOCUMENT CORRECTED
     • HOLD CARGO – DO NOT ACCEPT
     • REQUEST NEW HAWB
     • REMOVE PLASTIC COVERING HAZMAT LABELS

5. FINAL DECISION
   - One clear sentence:
     “Cargo may proceed once corrections are completed”
     OR
     “Cargo must be rejected until fully compliant”

STRICT RULES:
- Do NOT be vague
- Do NOT say “review” without saying HOW
- If labels are hidden, handwriting illegible, documents inconsistent → this is NOT GREEN
- Use professional aviation language
- Assume this is a REAL shipment at MIA counter

Cargo documentation:
{dossier}
"""

    analysis = run_gemini(prompt) or run_openai(prompt)

    if not analysis:
        analysis = (
            "System advisory notice: Unable to process the document at this time. "
            "Please review documentation manually."
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
