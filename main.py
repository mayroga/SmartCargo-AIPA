import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), images: List[UploadFile] = File(None)):
    # INSTRUCCIÓN TÁCTICA Y BLINDAJE
    instruction = (
        f"You are the Senior Tactical Advisor for SMARTCARGO by MAY ROGA LLC. Answer in {lang}. "
        "MISSION: Provide 'Immediate Satisfaction' with practical, hands-on solutions for the entire logistics chain. "
        "TONE: High-speed, professional, technical but easy to understand. Provide hope and stability. "
        "CORE DIRECTIVE: Don't just analyze; solve. Tell them: 'Adjust this', 'Move that', 'Change this label'. "
        "LEGAL SHIELD: We are PRIVATE ADVISORS. Not IATA/TSA/DOT. We don't touch cargo. This is a technical suggestion, not a legal verdict. "
        "FORMAT: "
        "1. [TACTICAL ACTION PLAN] - Step-by-step to pass inspection NOW. "
        "2. [SOLUTIONS] - 🔴 Option A (Fastest), 🟡 Option B (Middle), 🟢 Option C (Structural). "
        "3. [RISK CHECK] - Identify errors in paperwork or cargo handling."
    )
    
    parts = [{"text": f"{instruction}\n\nISSUE TO SOLVE: {prompt}"}]
    
    # Intento con Gemini
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            if images:
                for img in images[:3]:
                    content = await img.read()
                    parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    # Backup con OpenAI (Requerimiento de redundancia)
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e: return {"data": f"Error: {str(e)}"}

    return {"data": "System connection error. Please try again."}

# Resto de rutas (create-payment, success, etc) se mantienen iguales...
