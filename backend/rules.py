# backend/rules.py

from typing import List, Dict
from storage import list_documents

# --------------------------------------
# Reglas Avianca-first (aceptación automática)
# --------------------------------------
# Define documentos obligatorios según Avianca Cargo
AVIANCE_REQUIRED_DOCS = [
    "Commercial Invoice",
    "Packing List",
    "AWB"
]

OPTIONAL_DOCS = [
    "Shipper's Letter of Instruction",
    "Certificado",
    "MSDS",
    "Permiso País Destino"
]

# Roles
ROLES = ["supervisor", "auditor", "admin", "user"]

def validate_cargo(cargo_id: int, role: str = "user") -> Dict:
    """
    Valida documentos de un cargo según reglas Avianca-first.
    - Aceptación automática si todos los obligatorios están presentes.
    - Incluye sugerencias de faltantes.
    """
    present_docs = [f.split("_")[0] for f in list_documents(cargo_id)]

    missing_required = [doc for doc in AVIANCE_REQUIRED_DOCS if doc not in present_docs]
    missing_optional = [doc for doc in OPTIONAL_DOCS if doc not in present_docs]

    status = "✅ Aceptado automáticamente" if not missing_required else "❌ Pendiente de revisión"
    detail = {
        "cargo_id": cargo_id,
        "role": role,
        "status": status,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "all_documents": present_docs
    }

    # Roles específicos pueden tener validaciones adicionales
    if role == "auditor" and missing_required:
        detail["status"] = "⚠ Requiere auditoría"

    return detail
