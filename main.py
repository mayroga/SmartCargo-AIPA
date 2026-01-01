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

@app.get("/")
async def home(): return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), cargo_type: str = Form("air"), images: List[UploadFile] = File(None)):
    # Instrucción Maestra para un Asesor Global
    instruction = (
        f"Eres el Asesor Senior Global de SMARTCARGO ADVISORY LLC. Responde en {lang}. "
        "TU PODER: Conoces todas las reglas legales de carga (Aéreo, Mar, Tierra) del MUNDO. "
        "Si el cliente menciona un país (ej. Australia, España, China), aplica sus leyes locales. "
        "Si no menciona país, asume USA/Florida (TSA/DOT/IATA). "
        "REGLAS OBLIGATORIAS: "
        "1. No menciones IA. Eres un experto humano. "
        "2. SEMÁFORO: 🔴 [ALERTA] para riesgo de rechazo, 🟢 [CUMPLIMIENTO] para carga segura. "
        "3. SOLUCIONES: Enfócate en que la carga fluya y el cliente ahorre dinero."
    )
    
    parts = [{"text": f"{instruction}\n\nModalidad: {cargo_type}\nConsulta: {prompt}"}]
    if images:
        for img in images[:3]:
            content = await img.read()
            if content:
                parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})

    # Prioridad Gemini 1.5 Flash (Análisis visual global rápido)
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    # Backup OpenAI GPT-4o
    if OPENAI_KEY:
        client = openai.OpenAI(api_key=OPENAI_KEY)
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}])
        return {"data": res.choices[0].message.content}
