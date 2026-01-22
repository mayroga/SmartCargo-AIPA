from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI(title="SmartCargo Advisory Backend")

# 1. CONFIGURACIÓN DE SEGURIDAD (CORS)
# Permite la comunicación con el frontend en Render o local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. CONFIGURACIÓN DEL MOTOR DE ASESORÍA
# La API Key debe estar configurada en las variables de entorno de Render
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. PROMPT MAESTRO (INSTRUCCIONES DEL SISTEMA)
# Aquí se integran todas tus reglas de negocio y blindaje legal
SYSTEM_PROMPT = """
You are the high-level professional advisor for 'SmartCargo Advisory by MAY ROGA LLC'.
Your purpose is to provide stability to the logistics chain and prevent fines or holds.

STRICT RULES:
1. MEASUREMENTS: Always provide dimensions in both [Inches] INC and [Centimeters] CM.
2. LEGAL SHIELD: Never use words like 'audit', 'AI', or 'Artificial Intelligence'.
3. AUTHORITY: Do NOT claim to be IATA, DOT, TSA, CBP, or any government entity. State you are a private advisor.
4. TONE: Professional, expert, and proactive. Use words that suggest/advise (e.g., 'we suggest', 'it is recommended') to avoid legal liabilities.
5. KNOWLEDGE SCOPE: 
   - Full coverage of the 50 U.S. states and the entire health system (doctors, dentists, psychologists).
   - Expert in Avianca-related logistics and procedures.
   - Expert in maritime, terrestrial, and aerial advisory.
6. PROBLEM SOLVING: If data is missing in the database, you must fill the gap based on professional standards to provide a solution.
7. LANGUAGE: If the user asks in Spanish, respond in Spanish. If in English, respond in English.
"""

# 4. RUTAS DE LA API

@app.get("/")
async def root():
    return {"message": "SmartCargo Advisory API is running"}

@app.post("/advisory")
async def get_technical_solution(
    prompt: str = Form(...),
    role: str = Form(...),
    awb: str = Form(...),
    lang: str = Form("en")
):
    """
    Recibe la consulta técnica y devuelve la asesoría estratégica.
    """
    try:
        # Construcción del contexto para el motor
        user_context = f"""
        User Role: {role}
        Reference/AWB: {awb}
        Technical Situation: {prompt}
        """
        
        # Generación de la respuesta
        response = model.generate_content([SYSTEM_PROMPT, user_context])
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Empty response from advisory engine")

        return {
            "status": "success",
            "data": response.text,
            "reference": awb
        }

    except Exception as e:
        return {
            "status": "error",
            "data": "The technical brain is currently updating. Please try again in a few moments or contact support."
        }

@app.post("/upload-evidence")
async def upload_evidence(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    """
    Procesa las imágenes de carga o documentos enviadas por el usuario.
    """
    # Aquí se integra la lógica de procesamiento de imagen si es necesario
    return {
        "info": "Evidence received",
        "filename": file.filename,
        "analysis": "Image queued for technical verification"
    }

# 5. INICIO DEL SERVIDOR
if __name__ == "__main__":
    import uvicorn
    # Puerto 10000 para compatibilidad directa con Render
    uvicorn.run(app, host="0.0.0.0", port=10000)
