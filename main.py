from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import httpx

app = FastAPI(title="SMARTCARGO-AIPA")

app.mount("/static", StaticFiles(directory="static"), name="static")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def call_ai_expert(prompt: str) -> str:
    # 1️⃣ Try Gemini first
    if GEMINI_API_KEY:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            params = {"key": GEMINI_API_KEY}

            r = httpx.post(url, headers=headers, params=params, json=payload, timeout=15)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    # 2️⃣ Fallback OpenAI
    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are SMARTCARGO-AIPA expert advisor."},
                    {"role": "user", "content": prompt}
                ]
            }
            r = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
            return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    return "SMARTCARGO-AIPA could not generate advisory at this moment."


@app.get("/", response_class=HTMLResponse)
def index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/validate")
async def validate_cargo(request: Request):
    data = await request.json()

    weight = data["weight"]
    height = data["height"]
    role = data["role"]

    oversized = height > 244
    overweight = weight > 4500

    if oversized or overweight:
        semaforo = "🔴 NOT ACCEPTABLE"
    else:
        semaforo = "🟢 ACCEPTABLE"

    prompt = f"""
You are a senior cargo expert for Avianca.
Role: {role}
Weight: {weight} kg
Height: {height} cm

Explain clearly if this cargo can be accepted,
what regulations apply (IATA, TSA, CBP),
and what corrections are required if not acceptable.
"""

    advisory = call_ai_expert(prompt)

    return JSONResponse({
        "semaforo": semaforo,
        "oversized": oversized,
        "overweight": overweight,
        "advisory": advisory,
        "legal": "SMARTCARGO-AIPA is a preventive advisory system and does not replace airline decisions."
    })
