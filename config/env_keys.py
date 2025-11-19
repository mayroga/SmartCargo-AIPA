import os

# ==============================================================================
# SMARTCARGO-AIPA BACKEND - CLAVES DE ENTORNO CRÍTICAS Y CONFIGURACIÓN (FIJAS)
# ==============================================================================

# --- 1. CLAVES DE ADMINISTRACIÓN Y ACCESO ---
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
BASE_URL = os.environ.get("BASE_URL") 
PORT = os.environ.get("PORT")

# --- 2. CONFIGURACIÓN DE BASE DE DATOS Y ENTORNO ---
DATABASE_URI = os.environ.get("DATABASE_URI")
NODE_ENV = os.environ.get("NODE_ENV") 

# --- 3. CLAVES DE PAGO (STRIPE) ---
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
# Corregido: Usar variable de entorno para la clave pública
STRIPE_PUBLISHABLE_KEY_PUBLIC = os.environ.get("STRIPE_PUBLISHABLE_KEY")

# --- 4. CLAVES DE IA Y COMUNICACIÓN ---
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
