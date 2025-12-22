import os
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from google import genai
from google.genai import types

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# INSTRUCCIÓN DE ÉLITE: SOLUCIÓN, AHORRO Y RECTIFICACIÓN
SYSTEM_RULES = """
ROLE: SENIOR LOGISTICS ADVISOR (PROBLEM SOLVER).
MISSION: Provide the fastest, cheapest, and safest technical solution to ensure cargo moves without delays.
STRICT RULES:
1. FOCUS: Provide RECTIFICATION steps for DG, ISPM-15, Strapping, and TSA compliance.
2. ECONOMY: Always suggest the most cost-effective way to fix the issue.
3. LIMIT: Exactly TWO (2) objective solutions. No warnings, just actions.
4. TONE: Helpful, efficient, and professional.
"""

@app.post("/advisory")
async def advisory(prompt: str = Form(...), image: UploadFile = File(None)):
    try:
        contents = [prompt]
        if image:
            img_bytes = await image.read()
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        
        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_RULES, max_output_tokens=300)
        )
        return {"data": res.text}
    except Exception:
        return {"data": "System ready. Please try your query again."}

@app.get("/")
async def index():
    return FileResponse('static/index.html')
