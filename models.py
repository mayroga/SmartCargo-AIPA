from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, create_engine, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()
DATABASE_URL = "sqlite:///./smartcargo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Cargo(Base):
    __tablename__ = "cargos"
    id = Column(Integer, primary_key=True, index=True)
    mawb = Column(String, nullable=False, unique=True)
    hawb = Column(String)
    airline = Column(String, default="Avianca Cargo")
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    cargo_type = Column(String, nullable=False)
    flight_date = Column(DateTime, nullable=False)
    weight = Column(Float, default=0)
    volume = Column(Float, default=0)
    length = Column(Float, default=0)
    width = Column(Float, default=0)
    height = Column(Float, default=0)
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
    audit_notes = Column(String)
    cargo = relationship("Cargo", back_populates="documents")

Base.metadata.create_all(bind=engine)
