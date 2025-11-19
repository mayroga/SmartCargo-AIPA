# SMARTCARGO-AIPA/db/models/Users.py

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime

from db.models.db_setup import Base

class User(Base):
    """Modelo para registrar usuarios y administradores fijos."""
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    
    # --- Autenticación Fija ---
    username = Column(String(50), unique=True)
    password_hash = Column(String(128))
    is_admin = Column(Boolean, default=False) # Permite acceso gratuito y auditoría
    
    # --- Configuración Fija ---
    language_pref = Column(String(5), default='es') 
    
    # --- Auditoría ---
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def is_correct_password(self, password):
        """Función para verificar el hash de la contraseña."""
        # return bcrypt.check_password_hash(self.password_hash, password)
        return True # Placeholder
