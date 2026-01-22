# storage.py

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Document, Cargo
import boto3
from botocore.exceptions import ClientError

# -------------------
# Configuración S3
# -------------------
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "my-bucket")
S3_PREFIX = os.getenv("S3_PREFIX", "uploads/")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

if USE_S3:
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

# -------------------
# Carpeta local (fallback)
# -------------------
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

# -------------------
# Funciones
# -------------------
def generate_version() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")

def save_document(db: Session, file, cargo_id: int, doc_type: str, uploaded_by: str) -> Document:
    if doc_type not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo de documento '{doc_type}' no permitido")

    cargo: Cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise ValueError(f"Cargo ID '{cargo_id}' no existe")

    # Versionado automático
    version = generate_version()
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (" ", ".", "_")).rstrip()
    filename = f"{doc_type}_{version}_{safe_filename}"

    # Guardar en S3 o local
    if USE_S3:
        s3_key = f"{S3_PREFIX}{cargo_id}/{filename}"
        try:
            s3_client.upload_fileobj(file.file, S3_BUCKET, s3_key)
        except ClientError as e:
            raise Exception(f"No se pudo subir a S3: {e}")
    else:
        cargo_dir = BASE_DIR / str(cargo_id)
        cargo_dir.mkdir(parents=True, exist_ok=True)
        filepath = cargo_dir / filename
        with open(filepath, "wb") as f:
            f.write(file.file.read())

    # Crear registro en DB
    doc = Document(
        cargo_id=cargo_id,
        doc_type=doc_type,
        filename=filename,
        version=version,
        status="pending",
        responsible=uploaded_by,
        upload_date=datetime.utcnow(),
        audit_notes=f"Documento subido por {uploaded_by} a las {datetime.utcnow()}"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def list_documents(cargo_id: int) -> List[str]:
    if USE_S3:
        try:
            response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{S3_PREFIX}{cargo_id}/")
            return [obj["Key"].split("/")[-1] for obj in response.get("Contents", [])]
        except ClientError:
            return []
    else:
        cargo_dir = BASE_DIR / str(cargo_id)
        if not cargo_dir.exists():
            return []
        return [f.name for f in cargo_dir.iterdir() if f.is_file()]

def get_document_path(cargo_id: int, filename: str) -> str:
    if USE_S3:
        return f"s3://{S3_BUCKET}/{S3_PREFIX}{cargo_id}/{filename}"
    else:
        path = BASE_DIR / str(cargo_id) / filename
        if not path.exists():
            raise FileNotFoundError(f"Documento '{filename}' no encontrado para cargo '{cargo_id}'")
        return str(path)

def delete_document(db: Session, cargo_id: int, filename: str, deleted_by: str) -> bool:
    doc: Optional[Document] = db.query(Document).filter(
        Document.cargo_id == cargo_id,
        Document.filename == filename
    ).first()
    if not doc:
        return False

    # Borrar físico
    if USE_S3:
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=f"{S3_PREFIX}{cargo_id}/{filename}")
        except ClientError:
            return False
    else:
        path = BASE_DIR / str(cargo_id) / filename
        if path.exists():
            path.unlink()

    # Actualizar DB con auditoría
    doc.status = "deleted"
    doc.audit_notes = f"Documento eliminado por {deleted_by} a las {datetime.utcnow()}"
    db.commit()
    return True

def validate_documents(cargo_id: int, required_docs: List[str]) -> dict:
    present_docs = [f.split("_")[0] for f in list_documents(cargo_id)]
    missing = [doc for doc in required_docs if doc not in present_docs]
    status = "✔ Todos los documentos presentes" if not missing else "❌ Faltan documentos"
    return {"status": status, "missing": missing}
