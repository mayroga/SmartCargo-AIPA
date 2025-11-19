# SMARTCARGO-AIPA/db/models/Shipments.py

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime

from db.models.db_setup import Base

class Shipment(Base):
    __tablename__ = 'shipments'

    # PK: Corregido a UUID
    shipment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK: Corregido a UUID y apunta a users.user_id
    client_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    origin_city = Column(String, nullable=True) # Se deja nullable=True por si el endpoint no lo pide
    destination_city = Column(String, nullable=True) # Se deja nullable=True por si el endpoint no lo pide
    declared_value = Column(Float, nullable=True) # Se deja nullable=True por si el endpoint no lo pide
    is_dg = Column(Boolean, default=False)
    
    # --- Nuevas Columnas Agregadas (Necesarias para el endpoint /cargo/measurements) ---
    length_cm = Column(Float)
    width_cm = Column(Float)
    height_cm = Column(Float)
    weight_real_kg = Column(Float)
    shipper_name = Column(String)
    consignee_name = Column(String)
    airport_code = Column(String)
    commodity_type = Column(String)
    
    # Columnas de Estado y Auditoría
    is_wood_pallet = Column(Boolean, default=False)
    ispm15_conf = Column(Boolean, default=False)
    dg_risk_keywords = Column(String)
    service_tier = Column(String, default="NONE")
    legal_disclaimer_at_creation = Column(Text, nullable=False) # Inmutable para Reportes/Auditoría

    # Fechas y Estatus
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="PENDING")

    def __repr__(self):
        return f"<Shipment(id='{self.shipment_id}', client_id='{self.client_id}', status='{self.status}')>"
