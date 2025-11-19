# db/models/Reports.py

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime

# CORRECCIÓN: Se importa la clase Base
from db.models.db_setup import Base 

class Report(Base):
    """Modelo para guardar el registro inmutable de los reportes generados."""
    __tablename__ = 'reports'

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Asegura la FK con el Shipment corregido (UUID)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipments.shipment_id'), nullable=False)

    pdf_url = Column(String, nullable=False)
    
    # Textos legales inmutables para auditoría (Obligatorio)
    legal_disclaimer_core = Column(Text, nullable=False)
    legal_disclaimer_price = Column(Text, nullable=False)

    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
