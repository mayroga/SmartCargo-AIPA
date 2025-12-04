# src/logic/ia_validator.py
import os
from config.env_keys import GEMINI_API_KEY, LEGAL_DISCLAIMER_CORE
from requirements.legal.guardrails import PROHIBITED_ACTIONS_DG, PERMITTED_LEGAL_ADVICE
from requirements.standards.validation_codes import DG_KEYWORDS

# Nota: requiere google-genai en requirements si usas esa API
try:
    import google.genai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    GENAI_ENABLED = True
except Exception:
    GENAI_ENABLED = False

GUARDRAIL_PROMPT = (
    "Eres el asistente SmartCargo AIPA. Tu función es ASESORAR e INFORMAR, nunca clasificar, certificar "
    "ni declarar mercancía peligrosa. NUNCA menciones UN Numbers o clasificaciones oficiales. "
    f"Acciones prohibidas: {PROHIBITED_ACTIONS_DG}. Acciones permitidas: {PERMITTED_LEGAL_ADVICE}. "
    "Tu respuesta DEBE incluir siempre el siguiente descargo de responsabilidad al final: "
    f"'{LEGAL_DISCLAIMER_CORE}'"
)

def analyze_photo_and_dg(image_path, commodity_description):
    """
    Lógica que combina heurísticas con IA (si está disponible).
    Devuelve: {'ia_response': texto, 'dg_risk_level': 'BAJO'|'MEDIO'|'ALTO'}
    """
    # Heurística simple por keywords
    txt = (commodity_description or "").upper()
    dg_detected = any(k in txt for k in DG_KEYWORDS)

    # Nivel DG heurístico
    dg_risk = "ALTO" if dg_detected else "BAJO"

    # Si genai está configurado hacemos intento de llamada (no obligatoria)
    ia_text = "Análisis heurístico: " + ("Riesgo DG potencial detectado." if dg_detected else "No se detectaron indicios DG por descripción.")
    if GENAI_ENABLED:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=GUARDRAIL_PROMPT)
            # Componer prompt
            user_prompt = f"Analiza la descripción: {commodity_description}. ¿Hay señales de riesgo? Responde brevemente y añade el disclaimer."
            resp = model.generate_content(user_prompt)
            ia_text = resp.text
        except Exception as e:
            ia_text += f" (IA no disponible: {str(e)})"

    return {"ia_response": ia_text, "dg_risk_level": dg_risk, "legal_warning_fixed": LEGAL_DISCLAIMER_CORE}

def get_assistant_response(user_prompt):
    """
    Usa guardrail prompt para respuestas seguras.
    """
    if GENAI_ENABLED:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=GUARDRAIL_PROMPT)
        resp = model.generate_content(user_prompt)
        return resp.text
    # Fallback: respuesta simple instructiva
    return f"SmartCargo Assistant (offline): {user_prompt}\n\n{LEGAL_DISCLAIMER_CORE}"
