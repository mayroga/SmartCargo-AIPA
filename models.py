# models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)
    mawb = Column(String, nullable=False, unique=True)
    hawb = Column(String, nullable=True)
    airline = Column(String, default="Avianca Cargo")
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    cargo_type = Column(String, nullable=False)
    flight_date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, default="system")
    updated_by = Column(String, default="system")
    is_active = Column(Boolean, default=True)

    # Relación con documentos
    documents = relationship("Document", back_populates="cargo", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    doc_type = Column(String, nullable=False)  # Commercial Invoice, AWB, etc.
    filename = Column(String, nullable=False)  # Nombre físico en S3 o local
    version = Column(String, nullable=False, default="v1")  # Versionado automático
    status = Column(String, nullable=False, default="pending")  # pending, approved, rejected
    responsible = Column(String, nullable=False, default="user")  # Quien subió o revisó
    upload_date = Column(DateTime, default=datetime.utcnow)
    audit_notes = Column(String, nullable=True)  # Comentarios de auditoría

    cargo = relationship("Cargo", back_populates="documents")
