import os
import base64
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="SmartCargo AIPA - Technical Advisory")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# INSTRUCCIÓN DE BLINDAJE PROFESIONAL (ALCANCE DEL SERVICIO)
# Se define como "Third-Party Quality Control" para evitar temas de licencias oficiales.
SYSTEM_INSTRUCTION = """
ROLE: SENIOR TECHNICAL ADVISOR & QUALITY AUDITOR.
SCOPE: This system provides independent technical analysis based on international logistics standards (IATA, TSA, DGR). 
COMPLIANCE NOTICE: Our advisory is strictly informative. Final validation, classification, and acceptance 
remain the exclusive responsibility of the Certified Carrier, Regulated Agent (Forwarder), or Government Authority.
MISSION: Identify irregularities and provide professional technical recommendations for remediation.
TONE: Highly professional, objective, and technical.
LANGUAGE: Bilingual (English/Spanish).
"""

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: UploadFile = File(None)):
    img_bytes = await image.read() if image else None
    
    try:
        contents = [prompt]
        if img_bytes:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        
        res = client_gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        )
        
        # Blindaje elegante al final de cada respuesta
        disclaimer = "\n\n---\n*Technical Advisory Report: Subject to final verification by authorized entities.*"
        return {"data": res.text + disclaimer}
    except Exception as e:
        return {"data": "Technical service unavailable. Please retry."}

@app.post("/cargas")
async def process_audit(awb: str = Form(...), height: float = Form(...), ispm15: str = Form(...), unit: str = Form(...)):
    # Lógica de Auditoría: Problema -> Acción Recomendada
    reports = []
    score = 0
    H = height * 2.54 if unit == "in" else height

    if H > 158:
        reports.append({
            "issue": "AIRCRAFT CLEARANCE LIMIT EXCEEDED (>158cm).",
            "remediation": "RE-PACKING REQUIRED: Lower profile or specialized freighter booking (Main Deck)."
        })
        score += 50
    if ispm15 == "NO":
        reports.append({
            "issue": "REGULATORY WOOD COMPLIANCE RISK (ISPM-15).",
            "remediation": "IMMEDIATE ACTION: Swap to certified treated wood or synthetic pallet."
        })
        score += 40

    return {"score": min(score, 100), "reports": reports}

@app.get("/config")
async def get_config(): return {"status": "Operational", "mode": "Advisory"}
