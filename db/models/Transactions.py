# db/models/Transactions.py

from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime

# CORRECCIÓN: Se importa la clase Base
from db.models.db_setup import Base 

class Transaction(Base):
    """Modelo para registrar las transacciones de pago."""
    __tablename__ = 'transactions'

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Asegura la FK con el Shipment corregido (UUID)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipments.shipment_id'), nullable=False)
    
    stripe_session_id = Column(String(255), unique=True, nullable=False)
    price_paid = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    tier_purchased = Column(String(50)) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
