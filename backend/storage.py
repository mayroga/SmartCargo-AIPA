import os
from pathlib import Path
from datetime import datetime
from models import Document, SessionLocal

BASE_DIR = Path("storage/uploads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Tipos permitidos
TIPOS_DOCUMENTO = [
    "AWB", "Commercial Invoice", "Packing List", "MSDS", "DG Declaration",
    "Temperature Certificate", "Permiso País Destino"
]

def save_document(db, file_bytes: bytes, cargo_id: int, doc_type: str, uploaded_by: str):
    if doc_type not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo de documento '{doc_type}' no permitido")

    cargo_dir = BASE_DIR / str(cargo_id)
    cargo_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{doc_type}_{timestamp}.jpg"
    filepath = cargo_dir / filename

    # Guardar archivo
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    # Registrar en DB
    doc = Document(
        cargo_id=cargo_id,
        doc_type=doc_type,
        filename=filename,
        version=timestamp,
        status="✔ Válido",
        responsible=uploaded_by,
        upload_date=datetime.utcnow(),
        audit_notes=f"Documento cargado por {uploaded_by}"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def list_documents(cargo_id: int):
    cargo_dir = BASE_DIR / str(cargo_id)
    if not cargo_dir.exists():
        return []
    docs = []
    for f in cargo_dir.iterdir():
        if f.is_file():
            doc_type = f.name.split("_")[0]
            docs.append({"filename": f.name, "doc_type": doc_type, "status": "✔ Válido"})
    return docs
