from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)

    mawb = Column(String, nullable=False, index=True)
    hawb = Column(String, nullable=True)

    airline = Column(String, default="Avianca Cargo")
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)

    cargo_type = Column(String, nullable=False)  # GEN, DG, PER, AVI, HUM, VAL
    flight_date = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="cargo")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)

    doc_type = Column(String, nullable=False)  # Invoice, PL, MSDS, etc.
    status = Column(String, default="pending")  # valid / invalid / missing
    version = Column(String, nullable=False)
    responsible = Column(String, nullable=False)

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    cargo = relationship("Cargo", back_populates="documents")
