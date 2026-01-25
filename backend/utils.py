# utils.py
from rules import validate_cargo

def cargo_summary(cargo_id: int, role: str) -> dict:
    validation = validate_cargo(cargo_id)
    status = validation["status"]
    # Admin ve todos los detalles
    if role.lower() == "admin":
        return {"cargo_id": cargo_id, "status": status, "missing_docs": validation["missing_docs"]}
    else:
        return {"cargo_id": cargo_id, "status": status}
