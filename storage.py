# storage.py

import os
from pathlib import Path
from datetime import datetime
from typing import List
from backend.models import Document, Cargo

# Si quieres migrar a S3, puedes reemplazar BASE_DIR por boto3 bucket
BASE_DIR = Path("storage/uploads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Tipos de documentos permitidos por cargo
TIPOS_DOCUMENTO = [
    "Commercial Invoice",
    "Packing List",
    "Shipper's Letter of Instruction",
    "AWB",
    "Certificado",
    "MSDS",
    "Permiso País Destino"
]

# Roles del sistema
ROLES = ["user", "admin", "airline"]

def save_document(file, cargo_id: int, doc_type: str, uploaded_by: str, db_session) -> Document:
    """
    Guarda un documento, genera versión automática, registra auditoría y retorna Document.
    """
    if doc_type not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo de documento '{doc_type}' no permitido")

    # Carpeta del cargo
    cargo_dir = BASE_DIR / str(cargo_id)
    cargo_dir.mkdir(parents=True, exist_ok=True)

    # Generar nombre seguro con timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (" ", ".", "_")).rstrip()
    version = f"v{timestamp}"
    filename = f"{doc_type}_{version}_{safe_filename}"
    filepath = cargo_dir / filename

    # Guardar archivo físicamente
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    # Auditoría inicial
    audit = f"[{datetime.now().isoformat()}] Documento '{doc_type}' subido por '{uploaded_by}'\n"

    # Crear objeto Document en DB
    doc = Document(
        cargo_id=cargo_id,
        doc_type=doc_type,
        filename=filename,
        version=version,
        status="valid" if uploaded_by=="airline" and Cargo.airline=="Avianca Cargo" else "pending",
        uploaded_by=uploaded_by,
        upload_date=datetime.now(),
        audit_log=audit
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc

def list_documents(cargo_id: int) -> List[str]:
    """
    Lista nombres de archivos físicos de un cargo
    """
    cargo_dir = BASE_DIR / str(cargo_id)
    if not cargo_dir.exists():
        return []
    return [f.name for f in cargo_dir.iterdir() if f.is_file()]

def get_document_path(cargo_id: int, filename: str) -> Path:
    """
    Retorna ruta completa de un documento
    """
    path = BASE_DIR / str(cargo_id) / filename
    if not path.exists():
        raise FileNotFoundError(f"Documento '{filename}' no encontrado para cargo {cargo_id}")
    return path

def delete_document(cargo_id: int, filename: str) -> bool:
    """
    Elimina un documento y registra auditoría si existe
    """
    path = BASE_DIR / str(cargo_id) / filename
    if path.exists():
        path.unlink()
        return True
    return False

def validate_documents(cargo_id: int, required_docs: List[str]) -> dict:
    """
    Valida que todos los documentos requeridos estén presentes.
    """
    present_docs = [f.split("_")[0] for f in list_documents(cargo_id)]
    missing = [doc for doc in required_docs if doc not in present_docs]
    status = "✔ Todos los documentos presentes" if not missing else "❌ Faltan documentos"
    return {"status": status, "missing": missing}

def audit_document_update(doc: Document, action: str, performed_by: str, db_session):
    """
    Agrega un registro de auditoría a un documento
    """
    timestamp = datetime.now().isoformat()
    log = f"[{timestamp}] {action} por {performed_by}\n"
    doc.audit_log += log
    db_session.commit()

def role_can_edit(role: str, doc: Document) -> bool:
    """
    Control simple por roles: solo admin o airline pueden actualizar ciertos documentos
    """
    if role not in ROLES:
        return False
    if role=="user":
        return doc.status=="pending"
    if role in ["admin", "airline"]:
        return True
    return False
