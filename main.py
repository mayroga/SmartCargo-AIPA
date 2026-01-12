import os, stripe, httpx, urllib.parse
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Variables de Entorno
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

TECH_CORE = """
You are the Strategic Brain of SMARTCARGO ADVISORY by MAY ROGA LLC. 
OFFICIAL IDENTITY: High-level private logistics consultant. Not IATA, TSA, DOT, or Gov.
PHILOSOPHY: Mitigate holds and returns, maximize capital. 
RULES:
1. DUAL MEASURES: Always provide dimensions in [Inches] INC / [Centimeters] CM.
2. AUTHORITY: Professional, decisive, and interrogative. If info is missing, ask.
3. NO SYMBOLS: Do not use asterisks (*) or hashtags (#) for a clean voice reading.
4. THREAD: Maintain conversation flow to reach a resolution.
"""

@app.get("/")
async def home(): return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...), 
    history: Optional[str] = Form(""),
    lang: str = Form("es"), 
    role: Optional[str] = Form("auto")
):
    system_instr = f"{TECH_CORE}\nLanguage: {lang}. Role: {role}.\nCONTEXT: {history}\nQUERY: {prompt}"
    
    async with httpx.AsyncClient(timeout=40.0) as client:
        # --- PLAN A: GEMINI 1.5 FLASH (Prioridad por Velocidad) ---
        if GEMINI_KEY:
            try:
                url_g = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                res_g = await client.post(
                    url_g, 
                    json={"contents": [{"parts": [{"text": system_instr}]}]},
                    headers={"Content-Type": "application/json"}
                )
                if res_g.status_code == 200:
                    return {"data": res_g.json()["candidates"][0]["content"]["parts"][0]["text"]}
            except Exception as e:
                print(f"Gemini Error: {e}")

        # --- PLAN B: OPENAI GPT-4o (Respaldo de Emergencia) ---
        if OPENAI_KEY:
            try:
                res_o = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o",
                        "messages": [{"role": "system", "content": system_instr}],
                        "temperature": 0.3
                    }
                )
                if res_o.status_code == 200:
                    return {"data": res_o.json()["choices"][0]["message"]["content"]}
            except Exception as e:
                print(f"OpenAI Error: {e}")

    return {"data": "SMARTCARGO ERROR: No hay respuesta de los motores de IA. Verifica conexión y API Keys."}

# ... (El resto del código de pagos se mantiene igual)
