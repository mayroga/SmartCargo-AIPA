# SMARTCARGO-AIPA/db/models/Transactions.py

# ... (Importaciones necesarias: SQLAlchemy, UUID, etc.)

class Transaction(Base):
    """Modelo para registrar pagos fijos (Stripe)."""
    __tablename__ = 'transactions'

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipments.shipment_id'), nullable=False)
    stripe_session_id = Column(String(255), nullable=False)
    price_paid = Column(Float, nullable=False)
    status = Column(String(50), nullable=False) # Completed, Failed, Pending
    tier_purchased = Column(String(50), nullable=False) # LEVEL_BASIC (Fase 1)
    transaction_date = Column(DateTime, default=datetime.datetime.utcnow)
