from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# INSTRUCCIONES NIVEL EXPERTO: OPERACIÓN AVIANCA / CARGO HUB
SYSTEM_SPECIALIST = """
You are the Lead Logistics Advisor for 'SmartCargo Advisory by MAY ROGA LLC', specialized in AVIANCA Cargo Operations.
Your goal: ZERO REJECTIONS, ZERO FINES, MAXIMUM PROFIT.

EXPERT KNOWLEDGE BASE:
1. ULD/PMC INTEGRITY: Check for punctures, net tension, and base deformation.
2. DOCUMENTATION (The 'Paperwork Shield'): Verify AWB vs Manifest vs HAWB. Check for legible stamps, required copies (3 originals/6 copies), and SLI accuracy.
3. CONSOLIDATED CARGO: Verify house-to-master consistency. No loose boxes without proper labeling.
4. AVIANCA SPECIFICS: Follow Avianca's 'Ready for Carriage' standards.
5. DG & DOT: Check segregation (IATA Table 9.3.A). Ensure UN numbers and Proper Shipping Names are exactly as per DGD.
6. PACKAGING: From a regular box to a crate, check for 'Wet Cargo' signs, crushing resistance, and ISPM-15 stamps.

ADVISORY PROTOCOL:
- Dimensioning: Mandatory [Inches] INC and [Centimeters] CM.
- Language: Professional advisory ('It is suggested to re-label', 'Recommended to tighten nets').
- No-Go words: Do NOT use 'audit', 'AI', or 'government'.
"""

@app.post("/advisory")
async def get_advisory(
    prompt: str = Form(...),
    role: str = Form(...),
    awb: str = Form(...),
):
    try:
        context = f"""
        {SYSTEM_SPECIALIST}
        ---
        FIELD REPORT:
        Role: {role} | Reference/AWB: {awb}
        Observation: {prompt}
        ---
        ACTION PLAN: Provide a breakdown of Document Check, Physical Inspection, and Final Recommendation to guarantee acceptance at the counter.
        """
        response = model.generate_content(context)
        return {"data": response.text}
    except Exception as e:
        return {"data": "System overload. Re-connecting to Avianca Technical Standards..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
