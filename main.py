import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...), 
    lang: str = Form("en"), 
    cargo_type: str = Form("air"), 
    images: List[UploadFile] = File(None)
):
    # Instrucción Maestra con Blindaje Legal de MAY ROGA LLC
    instruction = (
        f"You are the Virtual Advisory Expert for MAY ROGA LLC. Respond strictly in {lang}. "
        "MANDATORY DISCLOSURE: You DO NOT certify, DO NOT inspect, and DO NOT replace regulators. "
        "You are a preventive advisor developed to protect merchandise through analysis and 100% automatic alerts. "
        "MAY ROGA LLC: NO touches/handles cargo, NO certifies DG, NO acts as TSA/IATA/IMO. "
        "Identify risks: 🔴 [ALERT] for rejection risks or 🟢 [COMPLIANCE] for safe flow. "
        "Be technical, helpful, and brief."
    )
    
    parts = [{"text": f"{instruction}\n\nCargo Mode: {cargo_type}\nUser Issue: {prompt}"}]
    
    if images:
        for img in images[:3]:
            content = await img.read()
            if content:
                parts.append({
                    "inline_data": {
                        "mime_type": img.content_type,
                        "data": base64.b64encode(content).decode("utf-8")
                    }
                })

    # Motor Principal: Gemini (Visión de alta precisión)
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    # Motor de Respaldo: OpenAI
    if OPENAI_KEY:
        client = openai.OpenAI(api_key=OPENAI_KEY)
        res = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
        )
        return {"data": res.choices[0].message.content}

    return JSONResponse(status_code=500, content={"error": "Engine error"})
