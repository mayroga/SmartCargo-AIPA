# main.py
import os
import json
import httpx
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ==============================
# APP CONFIG
# ==============================
app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")

# Monta carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Carpeta frontend
FRONTEND_DIR = Path(__file__).parent / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ==============================
# SERVIR FRONTEND
# ==============================
@app.get("/")
async def serve_index():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

# ==============================
# AI CORE
# ==============================
async def call_gemini(prompt: str):
    if not GEMINI_API_KEY:
        raise Exception("Gemini API Key not found")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents":[{"parts":[{"text":prompt}]}]}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def call_openai(prompt: str):
    if not OPENAI_API_KEY:
        raise Exception("OpenAI API Key not found")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "You are SMARTCARGO-AIPA, aviation cargo compliance expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

async def ai_engine(prompt: str):
    try:
        if GEMINI_API_KEY:
            return await call_gemini(prompt)
    except:
        pass
    if OPENAI_API_KEY:
        return await call_openai(prompt)
    return "AI engine unavailable"

# ==============================
# VALIDATE CARGO
# ==============================
@app.post("/validate")
async def validate_cargo(
    mawb: str = Form(...),
    hawb: str = Form(""),
    role: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    length: float = Form(...),
    width: float = Form(...),
    height: float = Form(...),
    dot: str = Form("No"),
    files: list[UploadFile] = File(default=[])
):
    # Calcula volumen m3
    volume_m3 = round((length * width * height)/1_000_000,3)

    # ==============================
    # VALIDACIÓN BASE (reglas físicas y documentos)
    # ==============================
    issues = []
    required_docs = ["AWB","Commercial Invoice","Packing List"]
    if cargo_type.upper() in ["DG","HAZMAT"]:
        required_docs += ["Shipper Declaration","MSDS"]

    if height > 244:
        issues.append("Height exceeds wide-body aircraft limit (244 cm)")
    if weight > 4500:
        issues.append("Weight exceeds pallet structural limit (4500 kg)")
    if len(files) < 1:
        issues.append("No photos uploaded (minimum 1 required)")

    # Semáforo
    semaforo = "RED" if issues else "GREEN"

    # ==============================
    # IA EXPERTO
    # ==============================
    prompt = f"""
You are SMARTCARGO-AIPA, aviation cargo compliance expert for Avianca.
ROLE: {role}
MAWB: {mawb}
HAWB: {hawb}
Origin: {origin}, Destination: {destination}
Cargo type: {cargo_type}, Weight: {weight} kg, Dimensions: {length}x{width}x{height} cm, Volume: {volume_m3} m3
DOT Declared: {dot}
Uploaded photos: {len(files)}

System findings: {issues if issues else 'No issues'}
Required documents: {required_docs}

TASK:
1. Explain clearly why this cargo is {semaforo}.
2. Include advisory actions if RED.
3. Include permanent legal disclaimer.
4. Be concise, operational, and authoritative.
5. Respond in English.
"""

    ai_result = await ai_engine(prompt)

    return JSONResponse({
        "status": semaforo,
        "volume_m3": volume_m3,
        "required_documents": required_docs,
        "issues": issues,
        "ai_advisor": ai_result,
        "files_uploaded": [f.filename for f in files],
        "disclaimer": "Preventive documentary validation system. Does not replace airline, TSA, CBP, DOT decisions."
    })
