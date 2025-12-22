import os
import stripe
import base64
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

load_dotenv()

FREE_ACCESS = True 

app = FastAPI(title="SmartCargo AIPA - Technical Advisor")

client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class CargoAudit(BaseModel):
    awb: str; length: float; width: float; height: float; weight: float
    ispm15_seal: str; unit_system: str; pkg_type: str

@app.post("/advisory")
async def advisory_vision(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    img_bytes = await image.read() if image else None
    
    # SYSTEM INSTRUCTION: EL ASESOR TOTAL
    instruction = """
    ROLE: PRE-SCREENING TECHNICAL ADVISOR (NOT TSA, NOT FORWARDER).
    MISSION: IDENTIFY IRREGULARITIES + PROVIDE IMMEDIATE SOLUTIONS.
    
    GUIDELINES:
    - BE BRIEF. Provide specific technical data (IATA/DGR standards).
    - TARGETS: Skids, Drums, Crates, Label Orientation, Stacking Risks.
    - ACTION: If you find a fault, you MUST provide the SOLUTION.
    - LIMITS: We do not move cargo, we do not certify for TSA. We advise on HOW to be compliant.
    - TONE: Professional, Expert, Bilingual.
    """

    try:
        contents = [prompt]
        if img_bytes:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        res = client_gemini.models.generate_content(
            model="gemini-2.0-flash", contents=contents,
            config=types.GenerateContentConfig(system_instruction=instruction, max_output_tokens=350)
        )
        return {"data": res.text}
    except:
        msgs = [{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
        res = client_openai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=350)
        return {"data": res.choices[0].message.content}

@app.post("/cargas")
async def process_audit(cargo: CargoAudit):
    # Lógica de Auditoría: Problema -> Solución
    reports = []
    score = 0
    H = cargo.height * 2.54 if cargo.unit_system == "in" else cargo.height
    
    if H > 158:
        reports.append({
            "issue": "HEIGHT EXCEEDS 158CM (NARROW-BODY LIMIT).",
            "solution": "Repack to lower height or book as MAIN DECK cargo on freighter aircraft."
        })
        score += 45
    if cargo.ispm15_seal == "NO":
        reports.append({
            "issue": "NON-COMPLIANT WOODEN PACKAGING.",
            "solution": "Swap to Plastic/Paper pallets or use ISPM-15 certified heat-treated wood."
        })
        score += 40
    if cargo.pkg_type == "Drum" and cargo.weight > 250:
        reports.append({
            "issue": "CONCENTRATED WEIGHT RISK.",
            "solution": "Place on a spreader board to distribute PSI on aircraft floor."
        })
        score += 15

    return {"score": min(score, 100), "reports": reports}
