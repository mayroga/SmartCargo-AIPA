# models.py
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

# =========================
# ENUMS
# =========================
class Role(str, Enum):
    SHIPPER = "SHIPPER"
    FORWARDER = "FORWARDER"
    TRUCKER = "TRUCKER"
    OWNER = "OWNER"
    COUNTER = "COUNTER"
    DG_OFFICER = "DG_OFFICER"

class CargoType(str, Enum):
    GENERAL = "GENERAL"
    PHARMA = "PHARMA"
    DG = "DG"
    VALUABLE = "VALUABLE"
    PERISHABLE = "PERISHABLE"
    HUMAN_REMAINS = "HUMAN_REMAINS"
    FULL_PALLET = "FULL_PALLET"

class AlertLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

# =========================
# PIECE / ITEM
# =========================
class CargoPiece(BaseModel):
    id: str
    cargo_type: CargoType
    weight_kg: float
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    height_m: Optional[float] = None
    temperature_c: Optional[float] = None
    description: Optional[str] = None

# =========================
# AWB / CARGO REQUEST
# =========================
class CargoRequest(BaseModel):
    role: Role
    shipment_number: str
    origin: str
    destination: str
    total_weight_kg: float
    total_pieces: int
    pieces: List[CargoPiece] = []
    documents: List[str] = []  # filenames of uploaded docs
    comments: Optional[str] = None

# =========================
# RULES / EVALUATION
# =========================
class CargoEvaluation(BaseModel):
    piece_id: Optional[str] = None
    alert: AlertLevel
    observation: str
