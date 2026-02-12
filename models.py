from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)
    mawb = Column(String, nullable=False)
    hawb = Column(String, nullable=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    cargo_type = Column(String, nullable=False)
    flight_date = Column(String, nullable=False)

    weight_kg = Column(Integer)
    volume_m3 = Column(Integer)
    length_cm = Column(Integer)
    width_cm = Column(Integer)
    height_cm = Column(Integer)

    role = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    documents = relationship(
        "Document",
        back_populates="cargo",
        cascade="all, delete-orphan"
    )

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id"))
    doc_type = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    description = Column(String, nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String, default="user")

    cargo = relationship("Cargo", back_populates="documents")
