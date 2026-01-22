# storage.py

import os
from datetime import datetime
from pathlib import Path
from typing import List

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

def save_document(file, cargo_id: str, doc_name: str) -> dict:
    """
    Guarda el archivo de manera segura y retorna metadata
    (la DB se maneja fuera de storage)
    """
    if doc_name not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo de documento '{doc_name}' no permitido")

    cargo_dir = BASE_DIR / str(cargo_id)
    cargo_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = "".join(
        c for c in file.filename if c.isalnum() or c in (" ", ".", "_")
    ).rstrip()

    filename = f"{doc_name}_{timestamp}_{safe_filename}"
    filepath = cargo_dir / filename

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return {
        "doc_type": doc_name,
        "filename": filename,
        "version": timestamp,
        "stored_path": str(filepath)
    }

def list_documents(cargo_id: str) -> List[str]:
    """
    Lista todos los documentos asociados a un cargo
    """
    cargo_dir = BASE_DIR / str(cargo_id)
    if not cargo_dir.exists():
        return []
    return [f.name for f in cargo_dir.iterdir() if f.is_file()]

def get_document_path(cargo_id: str, filename: str) -> Path:
    """
    Retorna la ruta completa de un documento
    """
    path = BASE_DIR / str(cargo_id) / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Documento '{filename}' no encontrado para cargo '{cargo_id}'"
        )
    return path

def delete_document(cargo_id: str, filename: str) -> bool:
    """
    Elimina un documento de manera segura
    """
    path = BASE_DIR / str(cargo_id) / filename
    if path.exists():
        path.unlink()
        return True
    return False

def validate_documents(cargo_id: str, required_docs: List[str]) -> dict:
    """
    Valida que todos los documentos obligatorios estén presentes
    """
    present_docs = [
        f.split("_")[0] for f in list_documents(cargo_id)
    ]

    missing = [doc for doc in required_docs if doc not in present_docs]

    return {
        "status": "OK" if not missing else "INCOMPLETE",
        "missing": missing,
        "present": present_docs
    }
