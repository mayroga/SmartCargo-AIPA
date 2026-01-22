# backend/utils.py

from backend.rules import validate_cargo

def cargo_summary(cargo, documents, role: str) -> dict:
    """
    Resumen para endpoint según rol
    """
    cargo_id = str(cargo.id)
    airline = cargo.airline

    validation = validate_cargo(cargo_id, airline, role)

    return {
        "cargo_id": cargo_id,
        "mawb": cargo.mawb,
        "hawb": cargo.hawb,
        "airline": airline,
        "origin": cargo.origin,
        "destination": cargo.destination,
        "cargo_type": cargo.cargo_type,
        "flight_date": cargo.flight_date.isoformat(),
        "status": validation["status"],
        "missing_docs": validation["missing_docs"],
        "all_docs": validation["all_docs"]
    }
