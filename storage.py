# backend/storage.py

import os
from datetime import datetime
from pathlib import Path
from typing import List
from models import Documento

# Carpeta base local para documentos (simula S3 / bucket)
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

def save_document(file, cargo_id: str, doc_name: str, uploaded_by: str) -> Documento:
    """
    Guarda el archivo de manera segura, genera versión, fecha y responsable.
    Retorna objeto Documento listo para motor de validación.
    """
    if doc_name not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo de documento '{doc_name}' no permitido")

    cargo_dir = BASE_DIR / cargo_id
    cargo_dir.mkdir(parents=True, exist_ok=True)

    # Generar nombre con timestamp para versionado
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (" ", ".", "_")).rstrip()
    filename = f"{doc_name}_{timestamp}_{safe_filename}"
    filepath = cargo_dir / filename

    try:
        with open(filepath, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise Exception(f"No se pudo guardar el documento: {e}")

    # Crear objeto Documento para trazabilidad
    doc = Documento(
        name=doc_name,
        status="✔ Válido",
        version=timestamp,
        upload_date=datetime.now(),
        uploaded_by=uploaded_by,
        filename=filename
    )

    return doc

def list_documents(cargo_id: str) -> List[str]:
    """
    Lista todos los documentos asociados a un cargo
    """
    cargo_dir = BASE_DIR / cargo_id
    if not cargo_dir.exists():
        return []
    return [f.name for f in cargo_dir.iterdir() if f.is_file()]

def get_document_path(cargo_id: str, filename: str) -> Path:
    """
    Retorna la ruta completa de un documento
    """
    path = BASE_DIR / cargo_id / filename
    if not path.exists():
        raise FileNotFoundError(f"Documento '{filename}' no encontrado para cargo '{cargo_id}'")
    return path

def delete_document(cargo_id: str, filename: str) -> bool:
    """
    Elimina un documento de manera segura (opcional para auditoría)
    """
    path = BASE_DIR / cargo_id / filename
    if path.exists():
        path.unlink()
        return True
    return False

def validate_documents(cargo_id: str, required_docs: List[str]) -> dict:
    """
    Valida que todos los documentos obligatorios estén presentes
    Retorna dict con estado y faltantes
    """
    present_docs = [f.split("_")[0] for f in list_documents(cargo_id)]
    missing = [doc for doc in required_docs if doc not in present_docs]
    status = "✔ Todos los documentos presentes" if not missing else "❌ Faltan documentos"
    return {"status": status, "missing": missing}
