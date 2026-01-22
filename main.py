from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# 1. CONFIGURACIÓN DE SEGURIDAD (CORS) - CRÍTICO PARA EVITAR BLOQUEOS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. RUTA RAÍZ (Evita el error "Not Found" al abrir la URL en el navegador)
@app.get("/")
async def root():
    return {
        "status": "Online",
        "system": "SmartCargo Advisory by MAY ROGA LLC",
        "specialty": "Avianca Cargo Operations"
    }

# 3. CONFIGURACIÓN DEL MOTOR DE INTELIGENCIA
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# EL CEREBRO: PROTOCOLO DE INSPECCIÓN TOTAL
SYSTEM_SPECIALIST = """
You are the Lead Logistics Advisor for 'SmartCargo Advisory by MAY ROGA LLC'.
Specialized in AVIANCA HUB operations. Goal: Zero rejections, Zero fines.

INSPECTION PROTOCOL:
1. ULD/PMC/AKE INTEGRITY: Check base, net tension, and contour for wide/narrow body.
2. DOCUMENT SHIELD: Legibility of AWB, Manifest, DGD, and SLI. Requirements: 3 originals, 6 copies.
3. VOLUMETRIC PROFIT: Compare Chargeable vs Actual. Use factor 6000 (CM) or 166 (INC).
4. IATA/DGR/DOT: Check Table 9.3.A for segregation. Verify UN numbers and labels.
5. PACKAGING: Regular boxes, crates, ISPM-15 stamps, and wet cargo protection.

STRICT MANDATES:
- Measurements: Always [Inches] INC and [Centimeters] CM.
- Legal: NEVER use 'audit', 'AI', 'Artificial Intelligence', or 'Government'.
- Tone: Suggestive expert ('We propose', 'It is recommended').
"""

# 4. RUTA DE ASESORÍA TÉCNICA
@app.post("/advisory")
async def get_advisory(
    prompt: str = Form(...),
    role: str = Form(...),
    awb: str = Form(...),
):
    try:
        # Combinamos el conocimiento experto con los datos del campo
        context = f"""
        {SYSTEM_SPECIALIST}
        ---
        FIELD REPORT:
        Role: {role}
        AWB/Ref: {awb}
        Observation/Data: {prompt}
        ---
        Deliver a professional 360° Technical Advisory.
        """
        
        response = model.generate_content(context)
        
        if not response.text:
            return {"data": "Incomplete field data. Please describe the cargo status better."}

        return {"data": response.text}
        
    except Exception as e:
        # Log del error interno (opcional)
        print(f"Error: {e}")
        return {"data": "The Technical Hub is recalibrating standards. Please retry in 10 seconds."}

if __name__ == "__main__":
    import uvicorn
    # Puerto 10000 para Render
    uvicorn.run(app, host="0.0.0.0", port=10000)
