# src/config/env_keys.py

import os

# Stripe
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Database
DATABASE_URI = os.getenv("DATABASE_URI", "")

# Render (opcional)
RENDER_API_KEY = os.getenv("RENDER_API_KEY", "")

# App config
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
