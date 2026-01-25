from pathlib import Path
from datetime import datetime
from backend.database import SessionLocal
from models import Document

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_document(cargo_id: int, doc_type: str, filename: str, description: str, uploaded_by: str):
    db = SessionLocal()
    try:
        doc = Document(
            cargo_id=cargo_id,
            doc_type=doc_type,
            filename=filename,
            description=description,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
    finally:
        db.close()


def list_documents(cargo_id: int):
    db = SessionLocal()
    try:
        return db.query(Document).filter(Document.cargo_id == cargo_id).all()
    finally:
        db.close()


def delete_document(cargo_id: int, filename: str, deleted_by: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(
            Document.cargo_id == cargo_id,
            Document.filename == filename
        ).first()

        if not doc:
            return False

        db.delete(doc)
        db.commit()
        return True
    finally:
        db.close()
