# SMARTCARGO-AIPA/db/models/db_setup.py

from sqlalchemy.orm import declarative_base

# Definición de la Base
Base = declarative_base()

# La configuración de la conexión (create_engine, sessionmaker) debe estar en un 
# archivo de inicialización de la aplicación o en la instancia de Flask-SQLAlchemy.
