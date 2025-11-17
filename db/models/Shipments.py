# SMARTCARGO-AIPA/db/models/Shipments.py

from config.env_keys import LEGAL_DISCLAIMER_CORE
from requirements.standards.validation_codes import ISPM_15_MARKS
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Shipment(Base):
    """Modelo para registrar los datos fijos de la carga y el cumplimiento legal."""
    __tablename__ = 'shipments'

    shipment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    
    # --- Medición Fija (6.1) ---
    length_cm = Column(Float, nullable=False)
    width_cm = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_real_kg = Column(Float, nullable=False)
    
    # --- Datos Fijos de AWB (7.0) ---
    shipper_name = Column(String(255), nullable=False)
    consignee_name = Column(String(255), nullable=False)
    airport_code = Column(String(3), nullable=False)
    
    # --- Compliance Legal Fijo (6.7) ---
    is_wood_pallet = Column(Boolean, default=False)
    ispm15_conf = Column(Boolean, default=False)
    
    # --- GUARDARRAÍL LEGAL (Inmutable, registro del texto exacto usado) ---
    legal_disclaimer_at_creation = Column(String, default=LEGAL_DISCLAIMER_CORE, nullable=False)
    
    service_tier = Column(String(50), default='LEVEL_BASIC')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
