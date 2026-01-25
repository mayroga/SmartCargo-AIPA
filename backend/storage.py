import os
from pathlib import Path
from datetime import datetime
from typing import List
from models import Document, SessionLocal

BASE_DIR = Path("storage/uploads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

TIPOS_DOCUMENTO = [
    "Commercial Invoice",
    "Packing List",
    "Shipper's Letter of Instruction",
    "AWB",
    "Health Certificate",
    "MSDS",
    "DGD"
]

def save_document(db, file, cargo_id: int, doc_type: str, uploaded_by: str) -> Document:
    if doc_type not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo de documento '{doc_type}' no permitido")
    cargo_dir = BASE_DIR / str(cargo_id)
    cargo_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (" ", ".", "_")).rstrip()
    filename = f"{doc_type}_{timestamp}_{safe_filename}"
    filepath = cargo_dir / filename
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    doc = Document(
        cargo_id=cargo_id,
        doc_type=doc_type,
        filename=filename,
        version=timestamp,
        status="🟢",
        responsible=uploaded_by,
        upload_date=datetime.utcnow()
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def list_documents(cargo_id: int) -> List[dict]:
    cargo_dir = BASE_DIR / str(cargo_id)
    if not cargo_dir.exists():
        return []
    docs = []
    for f in cargo_dir.iterdir():
        if f.is_file():
            parts = f.name.split("_")
            doc_type = parts[0]
            version = parts[1] if len(parts) > 2 else "v1"
            docs.append({"filename": f.name, "doc_type": doc_type, "version": version, "status": "🟢"})
    return docs

def delete_document(db, cargo_id: int, filename: str, deleted_by: str) -> bool:
    path = BASE_DIR / str(cargo_id) / filename
    if path.exists():
        path.unlink()
        doc = db.query(Document).filter_by(cargo_id=cargo_id, filename=filename).first()
        if doc:
            doc.status = "deleted"
            doc.audit_notes = f"Documento eliminado por {deleted_by}"
            db.commit()
        return True
    return False
