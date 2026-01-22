from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# ----------------------
# Documento
# ----------------------
class Documento(BaseModel):
    name: str  # Nombre del documento, ej: invoice, packingList
    status: str = "❌ Faltante"  # ✔ Válido / ⚠ Dudoso / ❌ Faltante
    version: Optional[str] = None  # Versión del documento
    upload_date: Optional[datetime] = None
    uploaded_by: Optional[str] = None  # Usuario que subió
    comment: Optional[str] = None  # Detalle de error o observación

# ----------------------
# Carga
# ----------------------
class Carga(BaseModel):
    airline: str
    mawb: str
    hawb: Optional[str] = None
    origin: str
    destination: str
    cargo_type: str  # GEN, DG, PER, HUM, AVI, VAL
    flight_date: datetime
    documents: List[Documento] = []

# ----------------------
# Resultado de Validación
# ----------------------
class ResultadoValidacion(BaseModel):
    status: str  # 🔴 NO ACEPTABLE / 🟡 ACEPTABLE CON RIESGO / 🟢 LISTA PARA ACEPTACIÓN
    documents: List[Documento]
    reason: Optional[str] = None
    timestamp: datetime = datetime.now()

# ----------------------
# Usuario / Rol
# ----------------------
class Usuario(BaseModel):
    username: str
    role: str  # dueñ@, forwarder, camionero, warehouse, admin
