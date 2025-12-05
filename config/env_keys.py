import os

# Stripe
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Base de datos
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://user:password@localhost:5432/SmartCargo-AIPA")

# Render
RENDER_API_KEY = os.getenv("RENDER_API_KEY", "")

# Admin
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# URL base para redirecciones
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# Opcional para emails o API externa
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "")
