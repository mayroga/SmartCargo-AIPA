import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")
@app.get("/app.js")
async def serve_js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en")):
    # INSTRUCCIÓN DE ÉLITE: PROHIBIDO USAR "AUDIT" / "AUDITORÍA"
    instruction = (
        "You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). "
        "Identity: PRIVATE TECHNICAL ADVISORS. Not IATA/TSA/DOT. "
        "Purpose: Prevent fines and holds so the paying customer never loses money. "
        "IMPORTANT: Never use the words 'audit', 'auditor', or 'auditing'. Use 'Technical Review', 'Strategic Analysis' or 'Verification'. "
        "NARRATIVA: Soluciones técnicas directas al pecho. No menciones IA. "
        "EXCELENCIA ESCALADA: Tier $5 (Courier), $15 (Standard), $35 (Critical Shield), $95 (Project Master). "
        "Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": [{"text": f"{instruction}\n\nClient Input: {prompt}"}]}]}, timeout=7.0)
            res = r.json()
            if 'candidates' in res: return {"data": res['candidates'][0]['content']['parts'][0]['text']}
            raise Exception()
    except:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}], timeout=12.0)
            return {"data": res.choices[0].message.content}
    return {"data": "System busy. Retry."}
