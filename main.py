# main.py
import os
import json
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Claves de IA
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")


# ---------- IA CORE ----------
def smartcargo_ai(prompt: str) -> str:
    """
    SMARTCARGO-AIPA IA core: Gemini primero, OpenAI si falla.
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


# ---------- ROOT ----------
@app.get("/")
async def root():
    path = Path("frontend/index.html")
    if not path.exists():
        return JSONResponse({"error": "index.html not found"}, status_code=404)
    return FileResponse(path)


# ---------- VALIDATION ----------
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
    dot: str = Form(...)
):
    volume = round((length * width * height) / 1_000_000, 3)

    # --------- REGLAS DURAS ---------
    issues = []
    required_docs = ["AWB", "Commercial Invoice", "Packing List"]

    if cargo_type.lower() in ["dg", "hazmat"]:
        required_docs += ["Shipper Declaration", "MSDS"]

    if height > 244:
        issues.append("Height exceeds aircraft maximum limit (244 cm).")
    if weight > 4500:
        issues.append("Weight exceeds standard pallet structural limits.")
    if cargo_type.lower() in ["dg", "hazmat"] and dot.lower() != "yes":
        issues.append("Dangerous goods without DOT declaration.")

    semaforo = "🟢 ACCEPTABLE" if not issues else "🔴 NOT ACCEPTABLE"

    # --------- IA PROMPT ---------
    prompt = f"""
You are SMARTCARGO-AIPA, acting as an airline cargo expert. You do not mention AI.
LANGUAGE: en

DATA:
- Role: {role}
- MAWB: {mawb}
- HAWB: {hawb}
- Origin: {origin}
- Destination: {destination}
- Cargo type: {cargo_type}
- Weight: {weight} kg
- Dimensions: {length}x{width}x{height} cm
- Volume: {volume} m3
- DOT declared: {dot}

SYSTEM:
- Required documents per role: {required_docs}
- Technical issues: {issues}

TASK:
1. Explain clearly WHY this cargo is {semaforo}.
2. Reference Avianca/IATA/TSA/CBP rules naturally.
3. Provide corrective actions if NOT ACCEPTABLE.
4. Include a permanent legal disclaimer.
"""

    advisor_text = smartcargo_ai(prompt)

    return JSONResponse({
        "semaforo": semaforo,
        "volume": volume,
        "required_documents": required_docs,
        "technical_issues": issues,
        "advisor": advisor_text,
        "legal_notice": "Preventive Documentary Validation System. Does not replace airline, TSA, CBP, DOT or authority decisions."
    })
