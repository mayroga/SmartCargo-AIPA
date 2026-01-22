from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/smartcargo")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Cargo(Base):
    __tablename__ = "cargo"
    id = Column(Integer, primary_key=True, index=True)
    mawb = Column(String, nullable=False)
    hawb = Column(String)
    airline = Column(String, default="Avianca Cargo")
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    cargo_type = Column(String, nullable=False)  # GEN, DG, HUM, VAL, etc.
    flight_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="cargo")

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargo.id"))
    doc_type = Column(String)  # Invoice, PackingList, SLI, MSDS, etc.
    status = Column(String, default="pending")  # ✔ válido / ❌ inválido / ⚠ dudoso
    version = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    responsible = Column(String)

    cargo = relationship("Cargo", back_populates="documents")

Base.metadata.create_all(bind=engine)
