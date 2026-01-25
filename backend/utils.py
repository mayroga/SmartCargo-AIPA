from models import SessionLocal, Cargo
from backend.rules import validate_cargo

def cargo_dashboard(db, role: str):
    cargos = db.query(Cargo).all()
    summary = []
    for c in cargos:
        docs = [{"doc_type": d.doc_type, "status": d.status, "filename": d.filename} for d in c.documents]
        cargo_dict = {
            "cargo_id": c.mawb,
            "weight": c.weight,
            "volume": c.volume,
            "length": c.length,
            "width": c.width,
            "height": c.height,
            "cargo_type": c.cargo_type,
            "documents": docs
        }
        validation = validate_cargo(cargo_dict)
        cargo_dict.update(validation)
        summary.append(cargo_dict)
    return summary
