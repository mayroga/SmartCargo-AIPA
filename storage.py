# storage.py
import os
from datetime import datetime
from pathlib import Path
from typing import List
import boto3
from models import Document, Cargo, SessionLocal

# Carpeta local para backup
BASE_DIR = Path("storage/uploads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Configuración S3
S3_BUCKET = os.getenv("S3_BUCKET")
S3_CLIENT = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Tipos de documentos permitidos
TIPOS_DOCUMENTO = [
    "Commercial Invoice", "Packing List", "Shipper's Letter of Instruction",
    "AWB", "Certificado", "MSDS", "Permiso País Destino"
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

    # Guardar local
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    # Subir a S3 si configurado
    if S3_BUCKET:
        S3_CLIENT.upload_file(str(filepath), S3_BUCKET, f"{cargo_id}/{filename}")

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

def list_documents(cargo_id: int) -> List[str]:
    cargo_dir = BASE_DIR / str(cargo_id)
    if not cargo_dir.exists():
        return []
    return [f.name for f in cargo_dir.iterdir() if f.is_file()]

def get_document_path(cargo_id: int, filename: str) -> Path:
    path = BASE_DIR / str(cargo_id) / filename
    if not path.exists():
        raise FileNotFoundError(f"Documento '{filename}' no encontrado")
    return path

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

def validate_documents(cargo_id: int, required_docs: List[str]) -> dict:
    present_docs = [f.split("_")[0] for f in list_documents(cargo_id)]
    missing = [doc for doc in required_docs if doc not in present_docs]
    status = "✔ Todos los documentos presentes" if not missing else "❌ Faltan documentos"
    return {"status": status, "missing": missing}
