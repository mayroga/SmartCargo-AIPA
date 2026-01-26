# main.py
import os
import httpx
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")

app.mount("/static", StaticFiles(directory="static"), name="static")

FRONTEND_DIR = Path(__file__).parent / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@app.get("/")
async def index():
    return FileResponse(INDEX_FILE)

# ---------- SMARTCARGO CORE ----------
async def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents":[{"parts":[{"text":prompt}]}]}
    async with httpx.AsyncClient(timeout=40) as c:
        r = await c.post(url, json=payload)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

async def call_openai(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "You are SMARTCARGO-AIPA, aviation cargo compliance advisor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=40) as c:
        r = await c.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

async def smartcargo_engine(prompt):
    try:
        if GEMINI_API_KEY:
            return await call_gemini(prompt)
    except:
        pass
    if OPENAI_API_KEY:
        return await call_openai(prompt)
    return "SMARTCARGO-AIPA advisory engine unavailable."

# ---------- VALIDATION ----------
@app.post("/validate")
async def validate(
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
    admin_user: str = Form(""),
    admin_pass: str = Form(""),
    files: list[UploadFile] = File(default=[])
):
    volume = round((length * width * height) / 1_000_000, 3)
    issues = []

    if height > 244:
        issues.append("Height exceeds wide-body aircraft maximum (244 cm).")
    if weight > 4500:
        issues.append("Weight exceeds pallet structural limit (4500 kg).")
    if not files:
        issues.append("No cargo photos provided.")

    status = "RED" if issues else "GREEN"

    is_admin = admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD

    prompt = f"""
SMARTCARGO-AIPA advisory.

ROLE: {role}
ADMIN MODE: {is_admin}

MAWB: {mawb}
HAWB: {hawb}
Route: {origin} → {destination}
Cargo: {cargo_type}
Weight: {weight} kg
Dimensions: {length}x{width}x{height} cm
Volume: {volume} m3
DOT Declared: {dot}

Findings: {issues if issues else "No discrepancies"}

TASK:
- If ADMIN: provide expert-level counter/warehouse guidance.
- If CLIENT: guide only on documentation and corrections.
- Explain acceptance status.
- Include legal disclaimer.
"""

    advisory = await smartcargo_engine(prompt)

    return JSONResponse({
        "status": status,
        "volume": volume,
        "issues": issues,
        "advisor": advisory,
        "photos": [f.filename for f in files],
        "disclaimer": "SMARTCARGO-AIPA is a preventive advisory system. Final acceptance decisions belong exclusively to the airline, TSA, CBP and DOT."
    })
