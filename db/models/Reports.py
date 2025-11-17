# SMARTCARGO-AIPA/db/models/Reports.py

# ... (Importaciones necesarias: SQLAlchemy, UUID, etc.)

class Report(Base):
    """Modelo para registrar el informe final y la evidencia legal inmutable."""
    __tablename__ = 'reports'

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipments.shipment_id'), nullable=False)
    
    # --- EVIDENCIA LEGAL INMUTABLE (Los textos exactos usados) ---
    legal_disclaimer_core = Column(Text, nullable=False)
    legal_disclaimer_price = Column(Text, nullable=False)
    
    pdf_url = Column(String, nullable=False) # URL del PDF generado
    status = Column(String(50), default='Generated')
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
