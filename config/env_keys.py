import os

# ==============================================================================
# SMARTCARGO-AIPA BACKEND - CLAVES DE ENTORNO Y CONSTANTES CRÍTICAS (FIJAS)
# NUNCA DEBEN CAMBIAR
# ==============================================================================

# --- CLAVES DE ENTORNO (De Environmental en Render) ---
# Claves Privadas de Stripe
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Claves de Comunicación e IA
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_API_KEY = os.environ.get("EMAIL_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")

# --- CLAVE PÚBLICA DE PAGO (Única que se puede exponer al Frontend) ---
STRIPE_PUBLISHABLE_KEY_PUBLIC = "pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz"

# --- MENSAJE LEGAL OBLIGATORIO (3.3) ---
LEGAL_DISCLAIMER_CORE = (
    "SmartCargo ofrece asesoría informativa. No es un servicio certificado IATA/TSA/FAA/DOT. "
    "No clasifica ni declara mercancía peligrosa. "
    "Para materiales regulados, consulte a un especialista DG certificado o a la aerolínea correspondiente."
)

# --- ORGANISMOS REGULATORIOS FIJOS (Sección 1, 6, 8) ---
REGULATORY_BODIES = ["IATA", "TSA", "FAA", "DOT"]
