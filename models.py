from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)
    mawb = Column(String, nullable=True)  # Master AWB
    hawb = Column(String, nullable=True)  # House AWB
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    cargo_type = Column(String, nullable=False, default="normal")  # perecederos, DG, normal
    avion = Column(String, nullable=False, default="belly/pax")  # Belly/PAX, Freighter
    alto_cm = Column(Integer, nullable=True)
    peso_guia = Column(Integer, nullable=True)
    peso_real = Column(Integer, nullable=True)
    dg_firmado = Column(String, nullable=True)  # yes / no
    temp_rango = Column(String, nullable=True)  # ok / fuera
    madera_nimf = Column(String, nullable=True)  # yes / no

    semaforo = Column(String, nullable=True)  # ROJO / AMARILLO / VERDE
    observaciones = Column(String, nullable=True)  # JSON o texto con observaciones
    solucion = Column(String, nullable=True)  # JSON o texto con acciones sugeridas

    role = Column(String, nullable=False, default="Shipper")

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relación con documentos
    documents = relationship(
        "Document",
        back_populates="cargo",
        cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id"))
    doc_type = Column(String, nullable=False)  # tipo de documento
    filename = Column(String, nullable=False)
    description = Column(String, nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String, default="user")

    cargo = relationship("Cargo", back_populates="documents")


class AdminLog(Base):
    """
    Guarda preguntas y respuestas realizadas por el admin
    """
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
