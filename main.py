from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json

app = FastAPI(title="SMARTCARGO-AIPA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# ---------- IA CORE (SMARTCARGO-AIPA) ----------

def smartcargo_ai(prompt: str) -> str:
    """
    Intenta Gemini primero, si falla usa OpenAI.
    El cliente JAMÁS ve el proveedor.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_KEY)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        except Exception:
            return "System error. Unable to validate cargo at this moment."

# ---------- VALIDATION ENDPOINT ----------

@app.post("/validate")
async def validate_cargo(
    mawb: str = Form(...),
    hawb: str = Form(...),
    role: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    length: float = Form(...),
    width: float = Form(...),
    height: float = Form(...),
    dot: str = Form(...),
):
    volume = round((length * width * height) / 1_000_000, 3)

    hard_fail = False
    reasons = []

    # --------- REGLAS DURAS (NO IA) ---------
    if height > 160:
        hard_fail = True
        reasons.append("Height exceeds standard aircraft belly limits.")

    if cargo_type.lower() in ["dg", "hazmat"] and dot.lower() != "yes":
        hard_fail = True
        reasons.append("Dangerous cargo without DOT declaration.")

    # --------- IA PROMPT ---------
    prompt = f"""
    You are SMARTCARGO-AIPA, a preventive documentary validation system.
    You do not approve cargo. You simulate an experienced airline cargo counter.

    DATA:
    Role: {role}
    MAWB: {mawb}
    HAWB: {hawb}
    Origin: {origin}
    Destination: {destination}
    Cargo Type: {cargo_type}
    Weight: {weight} kg
    Dimensions: {length} x {width} x {height} cm
    Volume: {volume} m3
    DOT Declared: {dot}

    TASK:
    - Determine operational acceptability.
    - Anticipate counter rejection reasons.
    - Give clear operational guidance.
    - Never promise acceptance.
    """

    ai_response = smartcargo_ai(prompt)

    if hard_fail:
        status = "RED"
    else:
        status = "YELLOW" if "risk" in ai_response.lower() else "GREEN"

    return JSONResponse({
        "status": status,
        "volume": volume,
        "reasons": reasons,
        "analysis": ai_response,
        "disclaimer": "Preventive Documentary Validation System. Does not replace airline decisions."
    })
