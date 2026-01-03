import os
import base64
import httpx
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import FileResponse
from typing import List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(""),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    # INSTRUCCIÓN: Escucha al cliente. Lo que él describe es la prioridad.
    system_instruction = (
        "You are the Technical Advisory Engine of SmartCargo by May Roga LLC. "
        "Acknowledge the photos provided. "
        "Your priority is the CUSTOMER'S DESCRIPTION (provided via text or voice). "
        "Use the photos to confirm what you can, but if they are unclear, rely on the customer's input. "
        "If information is missing, ask open questions to let the customer describe the condition. "
        "Provide technical risk mitigation solutions based on the combined data. "
        f"Respond in: {lang}."
    )

    parts = [{"text": f"{system_instruction}\n\nCustomer Description: {prompt}"}]

    if files:
        for img in files[:3]:
            content = await img.read()
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(content).decode("utf-8")
                }
            })

    # Cascada de modelos para asegurar respuesta
    models = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    async with httpx.AsyncClient() as client:
        for m in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={GEMINI_KEY}"
            try:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                res_data = r.json()
                if "candidates" in res_data:
                    return {"data": res_data["candidates"][0]["content"]["parts"][0]["text"]}
            except: continue

    return {"data": "Expert system is processing. Please ensure your description is detailed."}
