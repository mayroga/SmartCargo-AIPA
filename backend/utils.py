# backend/utils.py

from typing import List, Dict
from .rules import validate_cargo   # <- Import corregido con punto relativo
from models import Cargo, Document

def cargo_summary(cargo: Cargo, documents: List[Document], role: str = "user") -> Dict:
    """
    Genera resumen de un cargo para frontend según rol:
    - Status general de documentos
    - Cantidad por tipo
    - Faltantes
    """
    doc_types_present = [doc.doc_type for doc in documents]
    doc_count = {doc_type: doc_types_present.count(doc_type) for doc_type in set(doc_types_present)}

    # Validación por reglas Avianca-first
    validation = validate_cargo(cargo.id, role)

    summary = {
        "cargo_id": cargo.id,
        "mawb": cargo.mawb,
        "hawb": cargo.hawb,
        "airline": cargo.airline,
        "origin": cargo.origin,
        "destination": cargo.destination,
        "flight_date": cargo.flight_date,
        "cargo_type": cargo.cargo_type,
        "documents_count": doc_count,
        "validation_status": validation["status"],
        "missing_required": validation["missing_required"],
        "missing_optional": validation["missing_optional"],
        "role": role
    }

    return summary
