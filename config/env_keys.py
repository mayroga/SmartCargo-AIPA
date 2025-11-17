import os

# ==============================================================================
# SMARTCARGO-AIPA BACKEND - CLAVES DE ENTORNO CRÍTICAS Y CONFIGURACIÓN (FIJAS)
# NUNCA DEBEN CAMBIAR SUS LLAMADAS O VALORES FIJOS
# ==============================================================================

# --- 1. CLAVES DE ADMINISTRACIÓN Y ACCESO (NUEVAS) ---
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")  # URL base de la aplicación/API
PORT = os.environ.get("PORT")

# --- 2. CONFIGURACIÓN DE BASE DE DATOS Y ENTORNO (NUEVAS) ---
DATABASE_URI = os.environ.get("DATABASE_URI")
NODE_ENV = os.environ.get("NODE_ENV")  # Ej. 'production', 'development'

# --- 3. CLAVES DE PAGO (STRIPE) ---
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
# Clave pública fija (la única que se puede exponer)
STRIPE_PUBLISHABLE_KEY_PUBLIC = "pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz"

# --- 4. CLAVES DE IA Y COMUNICACIÓN (REPETIDAS, PERO NECESARIAS) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_API_KEY = os.environ.get("EMAIL_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")

# --- 5. MENSAJE LEGAL OBLIGATORIO Y ESTÁNDARES (FIJOS) ---
LEGAL_DISCLAIMER_CORE = (
    "SmartCargo ofrece asesoría informativa. No es un servicio certificado IATA/TSA/FAA/DOT. "
    "No clasifica ni declara mercancía peligrosa. "
    "Para materiales regulados, consulte a un especialista DG certificado o a la aerolínea correspondiente."
)
REGULATORY_BODIES = ["IATA", "TSA", "FAA", "DOT", "ISPM-15"]
