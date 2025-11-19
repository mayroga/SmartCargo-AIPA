# SMARTCARGO-AIPA/db/models/db_setup.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# ******* CRITICAL FIX FOR SQLALCHEMY 1.4 *******
# Importar explícitamente el dialecto psycopg para asegurar que se registra
# antes de que create_engine corra, previniendo el fallo al buscar psycopg2.
try:
    import sqlalchemy.dialects.postgresql.psycopg
except ImportError:
    # Esto solo debería suceder si psycopg no está instalado (lo cual no es el caso aquí)
    print("Warning: Could not import sqlalchemy.dialects.postgresql.psycopg")
# ***********************************************


# Define la clase base para la declaración de modelos ORM
Base = declarative_base()

# La URL de conexión debe venir de una variable de entorno de Render
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/defaultdb")

# CORRECCIÓN CLAVE para SQLAlchemy 1.4:
# 1. Reemplazamos el esquema para usar postgresql+psycopg
# 2. Si la URL no tiene el adaptador, forzamos el uso del dialecto psycopg
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
