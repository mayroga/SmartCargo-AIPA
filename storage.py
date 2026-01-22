import os
from datetime import datetime
from pathlib import Path
from models import Documento

# Carpeta base local (para pruebas)
BASE_DIR = Path("uploads")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def save_document(file, cargo_id: str, doc_name: str, uploaded_by: str) -> Documento:
    """
    Guarda el archivo, genera versión, fecha y responsable
    """
    cargo_dir = BASE_DIR / cargo_id
    cargo_dir.mkdir(exist_ok=True)

    # Nombre con versión timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{doc_name}_{timestamp}_{file.filename}"
    filepath = cargo_dir / filename

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    doc = Documento(
        name=doc_name,
        status="✔ Válido",
        version=timestamp,
        upload_date=datetime.now(),
        uploaded_by=uploaded_by
    )
    return doc

def list_documents(cargo_id: str):
    """
    Listar documentos de un cargo
    """
    cargo_dir = BASE_DIR / cargo_id
    if not cargo_dir.exists():
        return []
    return [f.name for f in cargo_dir.iterdir() if f.is_file()]

def get_document_path(cargo_id: str, filename: str):
    return BASE_DIR / cargo_id / filename
