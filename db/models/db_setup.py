# SMARTCARGO-AIPA/db/models/Transactions.py

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

# ******* CORRECCIÓN CLAVE: Importación de Base *******
# 'Base' se define en db_setup.py, y debe ser importada por todos los modelos.
from db.models.db_setup import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    # Clave Primaria (PK)
    id = Column(String, primary_key=True, index=True)

    # Referencias y Montos
    client_id = Column(String, ForeignKey('users.id'), nullable=False)
    shipment_id = Column(String, ForeignKey('shipments.id'), nullable=True) # Opcional si la transacción no es directa
    amount = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    
    # Estatus del Pago y Proveedor
    status = Column(String, default="PENDING") # Ej: PENDING, SUCCESS, FAILED
    provider = Column(String, default="STRIPE")
    provider_txn_id = Column(String, nullable=True) # ID de la transacción en Stripe

    # Fechas
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction(id='{self.id}', amount='{self.amount}', status='{self.status}')>"
