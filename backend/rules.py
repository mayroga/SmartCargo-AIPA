# rules.py
from storage import list_documents

# Requerimientos Avianca-first por tipo de carga
REQUIRED_DOCS_AVIANCA = [
    "Commercial Invoice",
    "Packing List",
    "Shipper's Letter of Instruction",
    "AWB"
]

def validate_cargo(cargo_id: int) -> dict:
    present_docs = [f['doc_type'] for f in list_documents(cargo_id)]
    missing = [doc for doc in REQUIRED_DOCS_AVIANCA if doc not in present_docs]

    # Semáforo operativo
    if missing:
        status = "🔴 NO ACEPTABLE"
    else:
        status = "🟢 LISTA PARA ACEPTACIÓN"

    return {"cargo_id": cargo_id, "status": status, "missing_docs": missing}
