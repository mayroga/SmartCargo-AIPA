from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# Configuración de CORS para evitar errores de conexión
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Gemini con instrucciones de SmartCargo
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# INSTRUCCIONES DE SEGURIDAD Y ESPECIALIDAD
SYSTEM_BRAIN = """
You are 'SmartCargo Advisory by MAY ROGA LLC'. 
OFFICIAL RULES:
1. FOCUS: Maritime, Terrestrial, and Aerial logistics advisor (Specialist in AVIANCA cargo).
2. COMPLIANCE: Expert in IATA DGR, CBP, DOT, and TSA regulations.
3. LEGAL: You are NOT a government body. Do NOT use words like 'audit', 'AI', or 'Intelligence'.
4. MEASUREMENTS: Always provide dimensions in BOTH [Inches] INC and [Centimeters] CM.
5. LIABILITY: Use advisory language: 'We suggest', 'It is recommended', 'Action proposed'.
6. SCOPE: Cover all 50 states and health systems. If data is missing, suggest a professional alternative.
7. STYLE: Professional, interesting, and precise. Never mix words or lose the thread.
"""

@app.post("/advisory")
async def get_advisory(
    prompt: str = Form(...),
    role: str = Form(...),
    awb: str = Form(...),
):
    try:
        # Estructura de la consulta para el motor
        context = f"""
        {SYSTEM_BRAIN}
        ---
        CLIENT DATA:
        Role: {role}
        AWB/Reference: {awb}
        Situation Found: {prompt}
        ---
        Please provide a professional technical solution including risks and step-by-step advice.
        """
        
        # Generar contenido sin bloquear el hilo principal
        response = model.generate_content(context)
        
        if not response.text:
            return {"data": "Incomplete data. Please provide more details about the cargo."}

        return {"data": response.text}

    except Exception as e:
        # Error amigable para evitar que el frontend se bloquee
        return {"data": "Technical interruption. Please retry in 30 seconds."}

if __name__ == "__main__":
    import uvicorn
    # Puerto estandar para Render
    uvicorn.run(app, host="0.0.0.0", port=10000)
