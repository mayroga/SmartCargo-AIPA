import os
import base64
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# --- BUSINESS LOGIC ---
FREE_ACCESS = True  # Set to False to enable Stripe $25/$80/$500
PHOTO_LIMIT = 3

app = FastAPI(title="SmartCargo AIPA - Technical Advisory")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# INSTRUCCIÓN DE BLINDAJE Y CONTROL
SYSTEM_PROMPT = """
ROLE: SENIOR TECHNICAL ADVISOR (PRE-SCREENING).
SCOPE: Independent analysis based on IATA/TSA standards. 
CONSTRAINTS: 
1. Maximum TWO (2) technical suggestions per response.
2. Be brief, objective, and understandable.
3. Tone must be SUGGESTIVE ("Recommended Remediation").
4. Focus: Structural integrity (Skids, Drums, Crates), Stacking, and Label orientation.
NOTICE: We are advisors, not a regulatory authority.
"""

# Store to track photo usage per AWB session
session_usage = {}

@app.post("/advisory")
async def technical_advisory(awb: str = Form(...), prompt: str = Form(...), image: UploadFile = File(None)):
    # Photo Limit Control
    current_usage = session_usage.get(awb, 0)
    if current_usage >= PHOTO_LIMIT:
        return {"data": "SESSION LIMIT REACHED: Maximum 3 images per payment. Please start a new session."}
    
    img_bytes = await image.read() if image else None
    try:
        contents = [prompt]
        if img_bytes:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
            session_usage[awb] = current_usage + 1
        
        res = client_gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, max_output_tokens=250)
        )
        
        disclaimer = "\n\n---\n*Professional Suggestion: Final acceptance subject to authorized carrier.*"
        return {"data": res.text + disclaimer, "remaining": PHOTO_LIMIT - session_usage[awb]}
    except Exception:
        return {"data": "Technical Service Unavailable. Please retry."}

@app.post("/audit-basic")
async def basic_audit(height: float = Form(...), ispm15: str = Form(...), unit: str = Form(...)):
    # Operational Check: Problem -> Suggested Solution
    reports = []
    h_cm = height * 2.54 if unit == "in" else height
    
    if h_cm > 158:
        reports.append({
            "issue": "HEIGHT EXCEEDS 158CM (62.2in).",
            "suggestion": "RE-PACK: Reduce height to under 158cm or use Main Deck freighter."
        })
    if ispm15 == "NO":
        reports.append({
            "issue": "NON-COMPLIANT WOOD (ISPM-15).",
            "suggestion": "RE-PALLETIZE: Use plastic pallet or heat-treated certified wood."
        })
    
    return {"reports": reports[:2]} # Forced limit of 2
