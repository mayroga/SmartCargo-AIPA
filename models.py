from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)
    mawb = Column(String, nullable=False, unique=True)
    hawb = Column(String, nullable=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    cargo_type = Column(String, nullable=False)
    flight_date = Column(DateTime, nullable=False)
    weight_kg = Column(Float, nullable=False)
    weight_lbs = Column(Float, nullable=False)
    length_cm = Column(Float, nullable=False)
    width_cm = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    documents = relationship("Document", back_populates="cargo", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    doc_type = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    version = Column(String, nullable=False, default="v1")
    status = Column(String, nullable=False, default="pending")
    responsible = Column(String, nullable=False, default="user")
    upload_date = Column(DateTime, default=datetime.utcnow)
    audit_notes = Column(String, nullable=True)

    cargo = relationship("Cargo", back_populates="documents")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Shipper, Forwarder, Chofer, Warehouse, Operador
    created_at = Column(DateTime, default=datetime.utcnow)
