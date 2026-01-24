# utils.py
from backend/rules import validate_cargo

def cargo_summary(cargo_id: int, role: str) -> dict:
    validation = validate_cargo(cargo_id)
    status = validation["status"]

    # Roles pueden ver detalles o solo status resumido
    if role.lower() == "admin":
        return {"cargo_id": cargo_id, "status": status, "missing_docs": validation["missing_docs"]}
    else:
        return {"cargo_id": cargo_id, "status": status}


backend/rules.py
# rules.py
from storage import list_documents

REQUIRED_DOCS_AVIANCA = [
    "Commercial Invoice", "Packing List", "AWB"
]

def validate_cargo(cargo_id: int) -> dict:
    present = [f.split("_")[0] for f in list_documents(cargo_id)]
    missing = [doc for doc in REQUIRED_DOCS_AVIANCA if doc not in present]
    status = "accepted" if not missing else "pending"
    return {"cargo_id": cargo_id, "status": status, "missing_docs": missing}
