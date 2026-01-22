from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# Seguridad CORS para evitar bloqueos entre Frontend y Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración del motor de análisis
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# EL CEREBRO: PROTOCOLO DE INSPECCIÓN TOTAL - MAY ROGA LLC
SYSTEM_SPECIALIST = """
You are the Lead Logistics Advisor for 'SmartCargo Advisory by MAY ROGA LLC'.
Your core mission is to protect the client's money and ensure ZERO rejections at AVIANCA terminals.

INSPECTION PROTOCOL:
1. ULD/PMC: Verify if it's a PMC (Pallet) or AKE (Container). Check net tension, base integrity, and contour for narrow/wide body aircraft.
2. DOCUMENT SHIELD: Review AWB (legibility), Manifest, DGD (Dangerous Goods Declaration), and SLI. Ensure 3 originals and 6 copies are present.
3. VOLUMETRIC PROFIT: Analyze Chargeable vs Actual weight. If the volume weight is higher, propose a packing technical solution to increase density.
4. IATA/DGR: Check segregation (Table 9.3.A). Ensure labels (Hazard/Handling) are not peeling and are in the correct position.
5. AVIANCA READY-FOR-CARRIAGE: If it's a consolidation, verify house-to-master consistency.

STRICT MANDATES:
- Dimensioning: Use ONLY [Inches] INC and [Centimeters] CM.
- Legal Shield: NEVER use 'audit', 'AI', 'Artificial Intelligence', or 'Government'.
- Tone: Suggestive expert ('We advise', 'Recommended action'). Propose solutions to make the cargo acceptable.
"""

@app.post("/advisory")
async def get_advisory(
    prompt: str = Form(...),
    role: str = Form(...),
    awb: str = Form(...),
):
    try:
        # Combinamos las instrucciones del sistema con la situación real reportada
        context = f"""
        {SYSTEM_SPECIALIST}
        ---
        FIELD DATA:
        Expert Role: {role}
        Ref/AWB: {awb}
        Observation: {prompt}
        ---
        Deliver a 360° Technical Advisory including: 
        1. Documentation Status.
        2. Physical Integrity & Volume Analysis.
        3. Final Strategic Recommendation to prevent rejections.
        """
        
        response = model.generate_content(context)
        return {"data": response.text}
        
    except Exception as e:
        return {"data": "HUB connection timeout. Verify AWB data and retry."}

if __name__ == "__main__":
    import uvicorn
    # Puerto 10000 para despliegue inmediato en Render o Railway
    uvicorn.run(app, host="0.0.0.0", port=10000)
