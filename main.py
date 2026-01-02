import os, base64, httpx, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def home(): return FileResponse("index.html")

@app.post("/advisory")
async def advisory(prompt: str = Form(...), lang: str = Form("en"), images: List[UploadFile] = File(None)):
    # INSTRUCCIÓN MAESTRA: COMPORTAMIENTO HUMANO Y BLINDAJE
    instruction = (
        f"You are the Senior Technical Consultant for SmartCargo ADVISORY BY MAY ROGA LLC. Respond strictly in {lang}. "
        "IMPORTANT: Never mention you are an AI or a machine. Act as a human logistics expert. "
        "BLINDAJE: You DO NOT certify, inspect, or replace regulators. You provide preventive suggestions. "
        "MAY ROGA LLC is a private firm, NOT a government agency. "
        "Analyze text AND/OR photos. Identify risks with 🔴 [ALERT] or 🟢 [SAFE]."
    )
    
    parts_gemini = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
    messages_openai = [{"role": "system", "content": instruction}, {"role": "user", "content": [{"type": "text", "text": prompt}]}]

    if images:
        for img in images[:3]:
            content = await img.read()
            if content:
                b64 = base64.b64encode(content).decode("utf-8")
                parts_gemini.append({"inline_data": {"mime_type": img.content_type, "data": b64}})
                messages_openai[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:{img.content_type};base64,{b64}"}})

    # INTENTO 1: GEMINI
    if os.getenv("GEMINI_API_KEY"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts_gemini}]}, timeout=40.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass 

    # INTENTO 2: OPENAI (Backup automático)
    if os.getenv("OPENAI_API_KEY"):
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            res = client.chat.completions.create(model="gpt-4o", messages=messages_openai)
            return {"data": res.choices[0].message.content}
        except: pass

    return JSONResponse(status_code=500, content={"error": "Service temporarily unavailable."})
