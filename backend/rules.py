# backend/rules.py

from storage import list_documents, validate_documents

# Documentos obligatorios por aerolínea
REQUIRED_DOCS = {
    "Avianca Cargo": [
        "Commercial Invoice",
        "Packing List",
        "AWB"
    ]
}

def validate_cargo(cargo_id: str, airline: str, role: str) -> dict:
    """
    Motor de validación de documentos por cargo
    """
    required = REQUIRED_DOCS.get(airline, [])
    docs_status = validate_documents(cargo_id, required)
    return {
        "cargo_id": cargo_id,
        "airline": airline,
        "role": role,
        "status": docs_status["status"],
        "missing_docs": docs_status["missing"],
        "all_docs": docs_status["present"]
    }
