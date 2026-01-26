from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os, math, requests

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")

app.mount("/static", StaticFiles(directory="static"), name="static")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LEGAL_DISCLAIMER = (
    "SMARTCARGO-AIPA is a preventive operational system. "
    "It does not replace airline, government, or regulatory decisions "
    "(Avianca, IATA, TSA, CBP, DOT). Final acceptance remains with authorities."
)

def calculate_volume(l, w, h):
    return round((l * w * h) / 1000000, 3)

def hard_rules(data):
    issues = []
    docs_required = ["AWB"]

    role = data["role"]
    cargo = data["cargo_type"]
    height = data["height"]
    weight = data["weight"]

    if role in ["Warehouse", "Counter", "Operator"]:
        if height > 244:
            issues.append("Height exceeds wide-body aircraft limits (244 cm).")
        if weight > 4500:
            issues.append("Weight exceeds pallet position limits (4,500 kg).")

    if cargo in ["DG", "HAZMAT"]:
        docs_required.append("DGD (IATA Dangerous Goods Declaration)")

    if cargo in ["PER"]:
        docs_required.append("Temperature Control Certificate")

    return issues, docs_required

def ai_advisor(prompt):
    headers = {"Content-Type": "application/json"}

    # Try Gemini
    if GEMINI_API_KEY:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=10,
            )
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            pass

    # Fallback OpenAI
    if OPENAI_API_KEY:
        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=10,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass

    return "Operational advisory unavailable. Please rely on regulatory checklist."

@app.get("/", response_class=HTMLResponse)
def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/cargo/validate")
async def validate(request: Request):
    data = await request.json()

    volume = calculate_volume(data["length"], data["width"], data["height"])
    issues, docs_required = hard_rules(data)

    missing_docs = [
        d for d in docs_required if d not in data.get("documents", [])
    ]

    if issues or missing_docs:
        status = "🔴 NOT ACCEPTABLE"
    elif docs_required:
        status = "🟡 CONDITIONAL"
    else:
        status = "🟢 ACCEPTABLE"

    prompt = f"""
    You are SMARTCARGO-AIPA operational advisor.
    Role: {data['role']}
    Cargo type: {data['cargo_type']}
    Issues: {issues}
    Missing documents: {missing_docs}
    Provide professional aviation cargo advice referencing Avianca, IATA, TSA, CBP.
    """

    advisory = ai_advisor(prompt)

    return JSONResponse({
        "status": status,
        "volume": volume,
        "issues": issues,
        "required_documents": docs_required,
        "missing_documents": missing_docs,
        "advisor": advisory,
        "legal": LEGAL_DISCLAIMER
    })
