# SMARTCARGO-AIPA/db/models/db_setup.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Define la clase base para la declaración de modelos ORM
Base = declarative_base()

# La URL de conexión debe venir de una variable de entorno de Render
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/defaultdb")

# CORRECCIÓN CLAVE:
# Reemplazamos los esquemas 'postgresql://' o 'postgres://' por 'postgresql+psycopg://'.
# Esto es necesario para indicarle a SQLAlchemy que use el driver Psycopg 3,
# que instalamos en requirements.txt.
if DATABASE_URL.startswith("postgresql://"):
    DIALECT_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DIALECT_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
else:
    DIALECT_URL = DATABASE_URL


# Creación del Engine de SQLAlchemy (usando la URL corregida)
engine = create_engine(DIALECT_URL)

# Creación de la sesión (para futuras operaciones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para crear las tablas si no existen
def create_all_tables():
    # Crea las tablas en el esquema de la base de datos
    Base.metadata.create_all(bind=engine)
