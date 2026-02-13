from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class CargoType(str, Enum):
    GENERAL = "GENERAL"
    DG = "DG"  # Dangerous Goods
    PER = "PERISHABLE"
    HUM = "HUMAN_REMAINS"
    ICE = "DRY_ICE"

class AlertLevel(str, Enum):
    GREEN = "🟢 VERDE"
    YELLOW = "🟡 AMARILLO"
    RED = "🔴 ROJO"

class CargoPiece(BaseModel):
    id: str
    type: CargoType
    dg_class: Optional[str] = None  # Ej: "8", "4.1", "3"
    weight_lb: float
    length_in: float
    width_in: float
    height_in: float
    pallet_type: str # WOOD, PLASTIC, METAL
    has_ispm15: bool = False
    soc_percent: Optional[float] = None # Solo para Litio

class CargoRequest(BaseModel):
    awb: str
    aircraft: str # "PAX" o "CGO"
    pieces: List[CargoPiece]
    is_usa_customer: bool = True
