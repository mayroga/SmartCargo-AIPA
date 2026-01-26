import os
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SMARTCARGO-AIPA")
app.mount("/static", StaticFiles(directory="static"), name="static")

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def smartcargo_ai(prompt: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_KEY)
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        except Exception:
            return "Error técnico en la validación."

@app.post("/validate")
async def validate_cargo(
    mawb: str = Form(...),
    role: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    length: float = Form(...),
    width: float = Form(...),
    height: float = Form(...),
    lang: str = Form("en")
):
    volume = round((length * width * height) / 1_000_000, 3)
    
    # Prompt de experto en cumplimiento
    prompt = f"""
    Eres SMARTCARGO-AIPA. Experto en IATA, DOT, TSA, CBP y regulaciones de Avianca Cargo.
    Idioma: {lang}. Rol del usuario: {role}.
    Datos: MAWB {mawb}, Tipo: {cargo_type}, Peso: {weight}kg, Dim: {length}x{width}x{height}cm.
    
    INSTRUCCIONES:
    1. Evalúa si cabe en aviones de pasajeros (altura max 160cm) o requiere carguero puro (A330F).
    2. Responde con lenguaje técnico, específico y de mucho peso.
    3. Usa TABLAS Markdown para mostrar límites de peso y dimensiones.
    4. NO menciones que eres una IA o modelo de lenguaje.
    5. Si es carga peligrosa, exige cumplimiento de DOT/IATA DGR.
    6. El tono debe ser de asesor experto preventivo.
    """

    ai_analysis = smartcargo_ai(prompt)
    
    # Lógica de semáforo
    status = "GREEN"
    if height > 160 or weight > 4000: status = "RED"
    elif "revisar" in ai_analysis.lower() or "warning" in ai_analysis.lower(): status = "YELLOW"

    return {
        "status": status,
        "analysis": ai_analysis,
        "volume": volume,
        "legal": "AVISO LEGAL: Este sistema es una validación documental preventiva. No sustituye la decisión final de la aerolínea ni de las autoridades gubernamentales."
    }
