# SMARTCARGO-AIPA/db/models/Shipments.py

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

# CORRECCIÓN CLAVE: Importación absoluta.
from db.models.db_setup import Base

class Shipment(Base):
    __tablename__ = 'shipments'

    # Clave Primaria (PK)
    id = Column(String, primary_key=True, index=True)

    # Datos del Cliente y Envío
    client_id = Column(String, ForeignKey('users.id'), nullable=False)
    origin_city = Column(String, nullable=False)
    destination_city = Column(String, nullable=False)
    declared_value = Column(Float, nullable=False)
    is_dg = Column(Boolean, default=False)  # Mercancía Peligrosa (Dangerous Goods)

    # Fechas y Estatus
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="PENDING")

    # Referencia a otras tablas (Ejemplo: User/Client)
    # owner = relationship("User", back_populates="shipments")

    def __repr__(self):
        return f"<Shipment(id='{self.id}', client_id='{self.client_id}', status='{self.status}')>"
