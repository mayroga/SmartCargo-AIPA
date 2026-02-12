from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
import uuid

# =========================
# ESTÁNDARES DE AUTORIDAD (ENUMS)
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
# MODELOS DE VALIDACIÓN TÉCNICA
# =========================

class CargoAnswer(BaseModel):
    """Estructura de entrada desde el Frontend"""
    answers: Dict[str, str]  # Ejemplo: {"q1": "ok", "q7": "fail"}
    operator: Optional[str] = "Counter_Default"
    cargo_type: Optional[CargoType] = CargoType.GENERAL

class ValidationResult(BaseModel):
    """Estructura de salida del reporte profesional"""
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
# LÓGICA ESTRUCTURAL DE CARGA (FÍSICA)
# =========================

class Dimensions(BaseModel):
    height_cm: float
    width_cm: float
    length_cm: float
    weight_kg: float

    @property
    def volume_cbm(self) -> float:
        return round((self.height_cm * self.width_cm * self.length_cm) / 1_000_000, 3)

    @property
    def is_pax_ok(self) -> bool:
        """Valida si cabe en aviones de pasajeros de Avianca (A320 familias)"""
        return self.height_cm <= 80

# =========================
# BASE DE DATOS TÉCNICA (SMARTCARGO KNOWLEDGE)
# =========================

AVIATION_LIMITS = {
    "NARROW_BODY": {
        "max_height": 80,
        "models": ["A319", "A320", "A321"],
        "authority": "Avianca Cargo Ground Ops Manual"
    },
    "WIDE_BODY_LOWER": {
        "max_height": 160,
        "models": ["A330", "A330F"],
        "authority": "IATA ULD Regulations"
    }
}

# Referencia de preguntas técnicas para auditoría interna
QUESTIONS_DB = [
    {"id": "q1", "cat": "DOCS", "desc": "MAWB original + 3 copias", "reg": "CBP/Avianca"},
    {"id": "q2", "cat": "DOCS", "desc": "HMAWB y Manifiesto coinciden", "reg": "CBP AMS"},
    {"id": "q3", "cat": "DOCS", "desc": "Factura y Packing List", "reg": "IATA"},
    {"id": "q4", "cat": "CBP", "desc": "EIN/Tax ID presente", "reg": "CBP"},
    {"id": "q5", "cat": "TSA", "desc": "Contenido coincidente físico/X-Ray", "reg": "TSA Security"},
    {"id": "q6", "cat": "SAFE", "desc": "Sello de camión intacto", "reg": "Chain of Custody"},
    {"id": "q7", "cat": "DIM", "desc": "Altura ≤ 80cm o ≤ 160cm", "reg": "Engineering"},
    {"id": "q8", "cat": "DIM", "desc": "Peso pie cuadrado ≤ 732 kg/m²", "reg": "Aircraft Floor Limit"},
    {"id": "q9", "cat": "SAFE", "desc": "Pallet stretch y red", "reg": "Flight Safety"},
    {"id": "q10", "cat": "DG", "desc": "DGD y Marcado UN", "reg": "IATA DGR / DOT"},
    {"id": "q11", "cat": "DG", "desc": "Etiquetas de Riesgo legibles", "reg": "IATA DGR"},
    {"id": "q13", "cat": "TEMP", "desc": "Termógrafo y Rango 2°C-8°C", "reg": "Pharma/Perishable"},
    {"id": "q15", "cat": "HUM", "desc": "Permiso Sanidad y Acta Defunción", "reg": "Biosecurity"},
    {"id": "q16", "cat": "HUM", "desc": "Ataúd hermético y caja exterior", "reg": "IATA TACT"}
]

# =========================
# UTILIDADES DE REPORTE
# =========================

def generate_report_id() -> str:
    """Genera un identificador único para trazabilidad legal"""
    return f"SCR-{uuid.uuid4().hex[:8].upper()}"

def get_legal_disclaimer() -> str:
    return (
        "Este informe de asesoría se emite bajo estándares de IATA, CBP, TSA y DOT. "
        "SMARTCARGO BY MAY ROGA LLC no reemplaza la autoridad final del Capitán de la aeronave, "
        "pero garantiza el cumplimiento previo en Counter para evitar multas y rechazos."
    )
