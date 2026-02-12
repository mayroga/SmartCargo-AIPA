from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
import uuid

# =========================
# ESTÁNDARES DE AUTORIDAD
# =========================

class AlertLevel(str, Enum):
    GREEN = "GREEN - LISTA PARA VUELO"
    YELLOW = "YELLOW - ACEPTACIÓN CONDICIONADA"
    RED = "RED - CARGA NO APTA"

class CargoType(str, Enum):
    GENERAL = "General Cargo"
    PERISHABLE = "Perishable"
    PHARMA = "Pharma"
    DG = "Dangerous Goods"
    HUMAN_REMAINS = "Human Remains"
    LIVE_ANIMALS = "Live Animals"

# =========================
# MODELOS DE ENTRADA / SALIDA
# =========================

class CargoAnswer(BaseModel):
    """Datos recibidos desde el Frontend"""
    answers: Dict[str, str] = Field(
        ..., example={"q1": "ok", "q7": "fail"}
    )
    operator: Optional[str] = "Counter_Default"
    cargo_type: CargoType = CargoType.GENERAL

class ValidationResult(BaseModel):
    """Reporte técnico profesional"""
    report_id: str
    timestamp: str
    operator: str
    cargo_type: str
    total_questions: int
    green: int
    yellow: int
    red: int
    status: AlertLevel
    recommendations: List[str]
    legal_note: str

# =========================
# MODELOS FÍSICOS (OPCIONAL)
# =========================

class Dimensions(BaseModel):
    height_cm: float
    width_cm: float
    length_cm: float
    weight_kg: float

    @property
    def volume_cbm(self) -> float:
        return round(
            (self.height_cm * self.width_cm * self.length_cm) / 1_000_000,
            3
        )

    @property
    def pax_height_ok(self) -> bool:
        return self.height_cm <= 80

# =========================
# LÍMITES AERONÁUTICOS
# =========================

AVIATION_LIMITS = {
    "NARROW_BODY": {
        "max_height_cm": 80,
        "aircraft": ["A319", "A320", "A321"],
        "authority": "Avianca Cargo GOM"
    },
    "WIDE_BODY_LOWER": {
        "max_height_cm": 160,
        "aircraft": ["A330", "A330F"],
        "authority": "IATA ULD Regulations"
    }
}

# =========================
# BASE DE CONOCIMIENTO SMARTCARGO
# =========================

QUESTIONS_DB = [
    {
        "id": "q1",
        "category": "DOCS",
        "description": "MAWB original legible + 3 copias",
        "tip": "Documento base para aceptación y archivo de estación.",
        "authority": "CBP / Avianca"
    },
    {
        "id": "q2",
        "category": "DOCS",
        "description": "HMAWB y Manifiesto coinciden 100%",
        "tip": "Discrepancias generan multas AMS.",
        "authority": "CBP AMS"
    },
    {
        "id": "q3",
        "category": "DOCS",
        "description": "Factura Comercial y Packing List",
        "tip": "Indispensable para valoración aduanera.",
        "authority": "IATA"
    },
    {
        "id": "q4",
        "category": "CBP",
        "description": "EIN / Tax ID de Shipper y Consignee",
        "tip": "Dato obligatorio para transmisión AMS.",
        "authority": "CBP"
    },
    {
        "id": "q5",
        "category": "TSA",
        "description": "Contenido coincide con inspección física/X-Ray",
        "tip": "Contenido no declarado = rechazo inmediato.",
        "authority": "TSA"
    },
    {
        "id": "q6",
        "category": "SECURITY",
        "description": "Sello de camión intacto",
        "tip": "Garantiza cadena de custodia.",
        "authority": "Chain of Custody"
    },
    {
        "id": "q7",
        "category": "DIMENSIONS",
        "description": "Altura ≤ 80cm (PAX) o ≤ 160cm (Carguero)",
        "tip": "Exceder altura impide el embarque.",
        "authority": "Engineering"
    },
    {
        "id": "q8",
        "category": "WEIGHT",
        "description": "Peso ≤ 732 kg/m²",
        "tip": "Evita daños estructurales en bodega.",
        "authority": "Aircraft Floor Limit"
    },
    {
        "id": "q9",
        "category": "SAFETY",
        "description": "Pallet stretch + red de seguridad",
        "tip": "Evita desplazamientos en vuelo.",
        "authority": "Flight Safety"
    },
    {
        "id": "q10",
        "category": "DG",
        "description": "DGD firmada y Marcado UN",
        "tip": "DG mal declarada genera multas federales.",
        "authority": "IATA DGR / DOT"
    },
    {
        "id": "q11",
        "category": "DG",
        "description": "Etiquetas de riesgo visibles",
        "tip": "Clave para segregación segura.",
        "authority": "IATA DGR"
    },
    {
        "id": "q13",
        "category": "TEMP",
        "description": "Termógrafo activo (2°C – 8°C)",
        "tip": "Fuera de rango genera Claims.",
        "authority": "Pharma / Perishable"
    },
    {
        "id": "q15",
        "category": "HUMAN_REMAINS",
        "description": "Permiso Sanidad + Acta Defunción",
        "tip": "Documento legal obligatorio.",
        "authority": "Biosecurity"
    },
    {
        "id": "q16",
        "category": "HUMAN_REMAINS",
        "description": "Ataúd hermético + caja exterior",
        "tip": "Prevención de fugas biológicas.",
        "authority": "IATA TACT"
    }
]

# =========================
# UTILIDADES
# =========================

def generate_report_id() -> str:
    return f"SCR-{uuid.uuid4().hex[:8].upper()}"

def get_legal_disclaimer() -> str:
    return (
        "Este informe se emite bajo estándares IATA, CBP, TSA y DOT. "
        "SMARTCARGO BY MAY ROGA LLC garantiza validación previa en Counter "
        "para reducir riesgos operacionales, multas y rechazos."
    )
