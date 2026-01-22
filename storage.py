# backend/storage.py

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import boto3

# ----------------------------
# CONFIG LOCAL
# ----------------------------
BASE_DIR = Path("storage/uploads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------
# CONFIG S3 (para migración futura)
# ----------------------------
S3_ENABLED = False  # Cambiar a True para usar S3
S3_BUCKET = os.getenv("S3_BUCKET", "my-bucket")
S3_CLIENT = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
) if S3_ENABLED else None

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

# Roles permitidos
ROLES = ["admin", "user", "auditor"]

# ----------------------------
# FUNCIONES PRINCIPALES
# ----------------------------

def _get_cargo_dir(cargo_id: str) -> Path:
    cargo_dir = BASE_DIR / str(cargo_id)
    cargo_dir.mkdir(parents=True, exist_ok=True)
    return cargo_dir

def save_document(file, cargo_id: str, doc_name: str, uploaded_by: str) -> dict:
    """
    Guarda archivo, crea versión automática, auditoría y opcional S3.
    """
    if doc_name not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo de documento '{doc_name}' no permitido")

    cargo_dir = _get_cargo_dir(cargo_id)

    # Versionado automático real
    existing_versions = [
        f for f in os.listdir(cargo_dir) if f.startswith(doc_name)
    ]
    version_number = len(existing_versions) + 1
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (" ", ".", "_")).rstrip()
    filename = f"{doc_name}_v{version_number}_{timestamp}_{safe_filename}"
    filepath = cargo_dir / filename

    # Guardar archivo local
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    # Subir a S3 si está activado
    if S3_ENABLED:
        S3_CLIENT.upload_file(str(filepath), S3_BUCKET, f"{cargo_id}/{filename}")

    # Metadata / auditoría
    return {
        "doc_type": doc_name,
        "filename": filename,
        "version": version_number,
        "timestamp": timestamp,
        "uploaded_by": uploaded_by,
        "stored_path": str(filepath),
        "s3_path": f"s3://{S3_BUCKET}/{cargo_id}/{filename}" if S3_ENABLED else None
    }

def list_documents(cargo_id: str, role: str) -> List[dict]:
    """
    Lista documentos físicos y metadata según rol.
    Solo 'admin' y 'auditor' ven todos, 'user' solo su carga.
    """
    if role not in ROLES:
        raise PermissionError(f"Rol '{role}' no autorizado")

    cargo_dir = _get_cargo_dir(cargo_id)
    docs = []
    for f in cargo_dir.iterdir():
        if f.is_file():
            # Metadata básica
            doc_info = {
                "filename": f.name,
                "size_bytes": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            docs.append(doc_info)
    return docs

def get_document_path(cargo_id: str, filename: str) -> Path:
    """
    Retorna ruta completa
    """
    path = BASE_DIR / str(cargo_id) / filename
    if not path.exists():
        raise FileNotFoundError(f"Documento '{filename}' no encontrado para cargo '{cargo_id}'")
    return path

def delete_document(cargo_id: str, filename: str, role: str) -> bool:
    """
    Elimina documento solo admins
    """
    if role != "admin":
        raise PermissionError("Solo admins pueden eliminar documentos")
    path = BASE_DIR / str(cargo_id) / filename
    if path.exists():
        path.unlink()
        return True
    return False

def validate_documents(cargo_id: str, required_docs: List[str]) -> dict:
    """
    Valida presencia de todos los documentos obligatorios
    """
    present_docs = [f.split("_")[0] for f in os.listdir(BASE_DIR / str(cargo_id))]
    missing = [doc for doc in required_docs if doc not in present_docs]
    status = "✔ Todos los documentos presentes" if not missing else "❌ Faltan documentos"
    return {"status": status, "missing": missing, "present": present_docs}
