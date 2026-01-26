# main.py
import os
import json
import httpx
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# ==============================
# APP CONFIG
# ==============================
app = FastAPI(
    title="SMARTCARGO-AIPA by May Roga LLC",
    description="Preventive Documentary Validation System · Does not replace airline or authority decisions",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ==============================
# API KEYS (Render ENV)
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GEMINI_API_KEY and not OPENAI_API_KEY:
    raise RuntimeError("No AI provider keys configured")

# ==============================
# ROOT
# ==============================
@app.get("/")
async def index():
    index_path = Path("frontend/index.html")
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

# ==============================
# AI CORE (Gemini → OpenAI fallback)
# ==============================
async def call_gemini(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def call_openai(prompt: str):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "You are SMARTCARGO-AIPA, an aviation cargo compliance expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

async def ai_engine(prompt: str):
    if GEMINI_API_KEY:
        try:
            return await call_gemini(prompt)
        except Exception:
            pass
    if OPENAI_API_KEY:
        return await call_openai(prompt)
    raise HTTPException(status_code=500, detail="No AI engine available")

# ==============================
# VALIDATION ENDPOINT
# ==============================
@app.post("/cargo/validate")
async def validate_cargo(
    request: Request,
    language: str = Form("en"),  # en | es
    mawb: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    flight_date: str = Form(...),
    role: str = Form(...),
    cargo_type: str = Form(...),
    weight_kg: float = Form(...),
    length_cm: float = Form(...),
    width_cm: float = Form(...),
    height_cm: float = Form(...),
    documents_json: str = Form("[]")
):
    try:
        documents = json.loads(documents_json)
    except Exception:
        documents = []

    volume_m3 = round((length_cm * width_cm * height_cm) / 1_000_000, 3)

    # ==============================
    # SYSTEM HARD RULES (NO IA)
    # ==============================
    issues = []
    required_docs = ["AWB", "Commercial Invoice", "Packing List"]

    if cargo_type.upper() in ["DG", "DANGEROUS GOODS", "HAZMAT"]:
        required_docs += ["Shipper Declaration", "MSDS"]

    if height_cm > 244:
        issues.append("Height exceeds wide-body aircraft acceptance limits (244 cm).")

    if weight_kg > 4500:
        issues.append("Weight exceeds standard pallet structural limits.")

    missing_docs = [
        d for d in required_docs
        if d not in [doc.get("type") for doc in documents]
    ]

    # ==============================
    # SEMAFORO
    # ==============================
    if missing_docs or issues:
        semaforo = "🔴 NOT ACCEPTABLE"
    else:
        semaforo = "🟢 ACCEPTABLE"

    # ==============================
    # AI PROMPT (REAL OPERATIONAL)
    # ==============================
    prompt = f"""
You are SMARTCARGO-AIPA, an aviation cargo compliance expert for Avianca.

Respond ONLY as SMARTCARGO-AIPA.
DO NOT mention AI, Gemini, OpenAI, or models.

LANGUAGE: {language}

CARGO DATA:
- MAWB: {mawb}
- Origin: {origin}
- Destination: {destination}
- Flight date: {flight_date}
- Role: {role}
- Cargo type: {cargo_type}
- Weight: {weight_kg} kg
- Dimensions: {length_cm} x {width_cm} x {height_cm} cm
- Volume: {volume_m3} m3

DOCUMENTS PROVIDED:
{documents}

SYSTEM FINDINGS:
- Missing documents: {missing_docs}
- Technical issues: {issues}

TASK:
1. Explain clearly WHY this cargo is {semaforo}.
2. Reference Avianca / IATA / TSA / CBP / DOT rules naturally.
3. Give a corrective action list if NOT ACCEPTABLE.
4. Include a permanent legal disclaimer.
5. Be concise, operational, and authoritative.
"""

    advisor_text = await ai_engine(prompt)

    # ==============================
    # RESPONSE
    # ==============================
    return JSONResponse({
        "semaforo": semaforo,
        "volume_m3": volume_m3,
        "required_documents": required_docs,
        "missing_documents": missing_docs,
        "technical_issues": issues,
        "advisor": advisor_text,
        "legal_notice": (
            "Preventive documentary validation system. "
            "Does not replace airline, airport, TSA, CBP, DOT, or authority decisions."
        )
    })
