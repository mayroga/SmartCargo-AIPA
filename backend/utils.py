import os
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =====================================
# Llamada a Gemini IA, fallback OpenAI
# =====================================
def call_ai_system(prompt: str):
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    url_gemini = "https://api.gemini.ai/v1/generate"

    try:
        # Gemini
        response = requests.post(url_gemini, headers=headers, json={"prompt": prompt})
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            raise Exception("Gemini failed, fallback OpenAI")
    except:
        # OpenAI fallback
        import openai
        openai.api_key = OPENAI_API_KEY
        try:
            completion = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=600
            )
            return completion.choices[0].text.strip()
        except Exception as e:
            return f"AI system error: {str(e)}"

# =====================================
# Genera mensaje de asesoramiento
# =====================================
def generate_advisor_message(cargo_data: dict, validation_status: dict) -> str:
    """
    Genera explicación completa, legal y operativa según el cargo, rol y reglas.
    """
    mawb = cargo_data.get("mawb")
    hawb = cargo_data.get("hawb")
    cargo_type = cargo_data.get("cargo_type")
    role = cargo_data.get("role")
    weight = cargo_data.get("weight_kg")
    l = cargo_data.get("length_cm")
    w = cargo_data.get("width_cm")
    h = cargo_data.get("height_cm")
    missing_docs = validation_status.get("missing_docs", [])
    semaforo = validation_status.get("semaforo")
    overweight = validation_status.get("overweight")
    oversized = validation_status.get("oversized")
    
    prompt = f"""
    Eres un especialista en logística aérea y cumplimiento de Avianca/IATA/TSA/CBP.
    Cargo: MAWB {mawb}, HAWB {hawb}, Tipo: {cargo_type}, Rol: {role}.
    Peso: {weight} kg, Dimensiones: {l}x{w}x{h} cm.
    Semáforo: {semaforo}.
    Documentos faltantes: {missing_docs}.
    Sobrepeso: {overweight}, Sobredimensiones: {oversized}.
    
    Genera un mensaje de asesor legal y operativo que explique:
    - Por qué el semáforo es 🟢, 🟡 o 🔴
    - Qué documentos faltan y por qué son críticos
    - Riesgos de sobrepeso o sobredimensiones
    - Cumplimiento de TSA, CBP, IATA, reglas Avianca
    - Cualquier recomendación para que la carga pueda subir al avión
    - Lenguaje profesional, claro, en español
    - Explicación completa, lista para enviar a cliente por WhatsApp o PDF
    """

    ai_message = call_ai_system(prompt)
    return ai_message

# =====================================
# Genera semáforo completo y explicación
# =====================================
def cargo_dashboard(cargo_data: dict, validation_status: dict) -> dict:
    """
    Devuelve el semáforo, lista de documentos requeridos, faltantes, sobrepeso, sobredimensiones
    """
    return {
        "semaforo": validation_status.get("semaforo"),
        "documents_required": validation_status.get("required_docs", []),
        "missing_docs": validation_status.get("missing_docs", []),
        "overweight": validation_status.get("overweight", False),
        "oversized": validation_status.get("oversized", False)
    }
