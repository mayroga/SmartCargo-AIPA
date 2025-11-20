# SMARTCARGO-AIPA/src/logic/ia_validator.py

import google.genai as genai
from config.env_keys import GEMINI_API_KEY, LEGAL_DISCLAIMER_CORE
# src/logic/ia_validator.py (COPIAR Y PEGAR - LÍNEA 5)

# --- Importaciones de Lógica ---
import google.genai as genai
from config.env_keys import GEMINI_API_KEY
# CORRECCIÓN: Intentar importar la ruta completa desde el nivel raíz del proyecto
from src.requirements.legal.guardrails import PROHIBITED_ACTIONS_DG, PERMITTED_LEGAL_ADVICE
# La línea anterior asume que la raíz es donde está 'src'.
# Si el PYTHONPATH=src funcionó, esta línea debería ser:
# from requirements.legal.guardrails import PROHIBITED_ACTIONS_DG, PERMITTED_LEGAL_ADVICE 

# Si el problema persiste, la única opción es subir el archivo.
from requirements.standards.validation_codes import INCOMPATIBLE_RISKS

# Inicialización de la IA con el guardarraíl legal estricto
genai.configure(api_key=GEMINI_API_KEY)
# El prompt es la capa de blindaje legal sobre la IA
GUARDRAIL_PROMPT = (
    "Eres el asistente SmartCargo AIPA. Tu función es ASESORAR e INFORMAR, nunca clasificar, certificar "
    "ni declarar mercancía peligrosa. NUNCA menciones UN Numbers o Clases DG (1-9). "
    f"Acciones prohibidas: {PROHIBITED_ACTIONS_DG}. Acciones permitidas: {PERMITTED_LEGAL_ADVICE}. "
    "Tu respuesta DEBE incluir siempre el siguiente descargo de responsabilidad al final: "
    f"'{LEGAL_DISCLAIMER_CORE}'."
)

def analyze_photo_and_dg(image_path, commodity_description):
    """
    Combina análisis visual y textual para detectar riesgos DG y defectos de embalaje.
    """
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=GUARDRAIL_PROMPT
    )
    
    # 1. Análisis de Imagen (6.4)
    # Simulación de carga de la imagen (usando una función de tu framework)
    # image = load_image(image_path) 
    
    # 2. Instrucción de Validación
    prompt = (
        f"Analiza esta imagen y la descripción '{commodity_description}'. "
        "Busca defectos visibles (caja rota, cinta negra, falta de etiquetas). "
        "Si la descripción sugiere DG (aerosol, litio, pintura), solo ADVIERTE. "
        "Mantén un tono sugerente, nunca negativo o acusatorio."
    )
    
    # Esta es una simulación de la llamada, ajusta según tu biblioteca de IA
    response = model.generate_content(prompt) # Asumiendo que la imagen se pasa aquí
    
    # 3. Extracción de Riesgos y Blindaje
    # (En la implementación real, usarías structured output, aquí devolvemos el texto procesado)
    
    # Detección simple de riesgo DG informativo (6.5)
    dg_risk = "ALTO" if "LITIO" in commodity_description.upper() or "QUÍMICO" in commodity_description.upper() else "BAJO"

    return {
        "ia_response": response.text,
        "dg_risk_level": dg_risk,
        "legal_warning_fixed": LEGAL_DISCLAIMER_CORE
    }

def get_assistant_response(user_prompt):
    """
    Endpoint para el asistente de chat (5.0), que siempre usa el GUARDRAIL_PROMPT.
    """
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=GUARDRAIL_PROMPT
    )
    
    response = model.generate_content(user_prompt)
    return response.text
