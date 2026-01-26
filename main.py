from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

# ===============================
# APP
# ===============================
app = FastAPI(title="SmartCargo-AIPA")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ===============================
# ENV
# ===============================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ===============================
# LEGAL SHIELD (CENTRAL)
# ===============================
LEGAL_DISCLAIMER = {
    "Spanish": (
        "SmartCargo-AIPA by May Roga LLC actúa exclusivamente como una plataforma "
        "de asesoría técnica y documental. No sustituimos ni reemplazamos decisiones "
        "de aerolíneas, autoridades aeroportuarias, aduanas ni entidades gubernamentales. "
        "Las validaciones emitidas son orientativas y preventivas, basadas únicamente en "
        "la información suministrada por el usuario. La responsabilidad final sobre la "
        "carga, su documentación y su presentación oficial recae exclusivamente en el usuario."
    ),
    "English": (
        "SmartCargo-AIPA by May Roga LLC operates strictly as a technical and documentary "
        "advisory platform. We do not replace or override decisions made by airlines, "
        "airport authorities, customs, or any governmental entity. All validations are "
        "preventive and advisory in nature, based solely on information provided by the user. "
        "Final responsibility for cargo, documentation, and official presentation remains "
        "entirely with the user."
    )
}

# ===============================
# AI HANDLERS
# ===============================
def analyze_with_gemini(text: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(text)
        return response.text

    except Exception as e:
        print("Gemini failed:", e)
        return None


def analyze_with_openai(text: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a cargo documentation validation advisor."},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content


# ===============================
# BUSINESS LOGIC
# ===============================
def semaforo_logic(analysis: str) -> str:
    text = analysis.lower()

    if any(w in text for w in ["prohibited", "forbidden", "not allowed", "rechazada"]):
        return "RED"
    if any(w in text for w in ["review", "conditional", "verify", "posible"]):
        return "YELLOW"
    return "GREEN"


# ===============================
# ROUTES
# ===============================
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/validate")
async def validate(
    role: str = Form(...),
    lang: str = Form(...),
    dossier: str = Form(...)
):
    prompt = f"""
You are acting as a cargo counter inspector.
Role: {role}
Language: {lang}

Analyze the following cargo documentation text.
Determine if the cargo is acceptable, conditional, or not acceptable.
Explain clearly in simple language.

DOCUMENT:
{dossier}
"""

    analysis = analyze_with_gemini(prompt)

    if not analysis:
        analysis = analyze_with_openai(prompt)

    status = semaforo_logic(analysis)

    return JSONResponse({
        "status": status,
        "analysis": analysis.strip(),
        "disclaimer": LEGAL_DISCLAIMER.get(lang, LEGAL_DISCLAIMER["English"])
    })


@app.post("/admin")
async def admin(
    username: str = Form(...),
    password: str = Form(...),
    question: str = Form(...)
):
    if username != "admin" or password != os.getenv("ADMIN_PASSWORD"):
        return JSONResponse({"answer": "Unauthorized"})

    answer = analyze_with_openai(question)
    return JSONResponse({"answer": answer})
