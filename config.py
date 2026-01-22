import os
from pathlib import Path

# ------------------------
# RUTAS Y ALMACENAMIENTO
# ------------------------
BASE_DIR = Path(os.environ.get("SC_BASE_DIR", "uploads"))
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Almacenamiento en la nube (opcional S3)
USE_S3 = os.environ.get("SC_USE_S3", "False") == "True"
S3_BUCKET = os.environ.get("SC_S3_BUCKET", "")
S3_REGION = os.environ.get("SC_S3_REGION", "")
S3_ACCESS_KEY = os.environ.get("SC_S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.environ.get("SC_S3_SECRET_KEY", "")

# ------------------------
# BASE DE DATOS
# ------------------------
DB_URL = os.environ.get("SC_DB_URL", "postgresql://user:password@localhost:5432/smartcargo")

# ------------------------
# MOTOR DE VALIDACIÓN
# ------------------------
# Tipos de carga Avianca-first
CARGA_TYPES = ["GEN", "DG", "PER", "HUM", "AVI", "VAL"]

# Países de destino críticos (ejemplo)
DESTINOS_REQUIEREN_MSDS = ["USA", "COL", "BRA"]

# ------------------------
# IA
# ------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# ------------------------
# OTROS PARÁMETROS
# ------------------------
MAX_FILE_SIZE_MB = 50  # límite de documento
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".xlsx", ".jpg", ".png"]
