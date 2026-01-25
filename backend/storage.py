import os
from datetime import datetime
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from models import Document

# Carpeta local para documentos
BASE_DIR = Path("storage/uploads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Tipos de documentos permitidos
TIPOS_DOCUMENTO = [
    "Commercial Invoice",
    "Packing List",
    "Shipper's Letter of Instruction",
    "AWB",
    "Certificado",
    "MSDS",
    "Permiso País Destino"
]

def save_document(db: Session, file, cargo_id: str, doc_type: str, uploaded_by: str) -> Document:
    """
    Guarda un documento localmente y lo registra en la base de datos.
    """
    if doc_type not in TIPOS_DOCUMENTO:
        doc_type = "Otro"

    cargo_dir = BASE_DIR / str(cargo_id)
    cargo_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (" ", ".", "_")).rstrip()
    filename = f"{doc_type}_{timestamp}_{safe_filename}"
    filepath = cargo_dir / filename

    with open(filepath, "wb") as f:
        f.write(file.file.read())

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
