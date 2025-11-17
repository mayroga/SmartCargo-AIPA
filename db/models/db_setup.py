# SMARTCARGO-AIPA/db/models/db_setup.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Define la clase base para la declaración de modelos ORM
Base = declarative_base()

# La URL de conexión debe venir de una variable de entorno de Render
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/defaultdb")

# Creación del Engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Creación de la sesión (para futuras operaciones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para crear las tablas si no existen
def create_all_tables():
    # Solo crea las tablas en el esquema de la base de datos
    Base.metadata.create_all(bind=engine)

# Nota: Esta función debe ser llamada en tu archivo principal (endpoints.py)
# antes de que la aplicación empiece a recibir solicitudes.
