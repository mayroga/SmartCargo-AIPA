from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import uuid

# =========================
# ENUMS
# =========================

class AlertLevel(str, Enum):
    GREEN = "CUMPLE - LISTA PARA VUELO"
    YELLOW = "OBSERVACIÓN - ACEPTACIÓN CONDICIONADA"
    RED = "RECHAZO - CARGA NO APTA"

class CargoType(str, Enum):
    GENERAL = "General Cargo"
    PERISHABLE = "Perishable"
    PHARMA = "Pharma"
    DG = "Dangerous Goods"
    HUMAN_REMAINS = "Human Remains"
    LIVE_ANIMALS = "Live Animals"

# =========================
# MODELOS
# =========================

class CargoAnswer(BaseModel):
    answers: Dict[str, str] = Field(..., example={"q1":"ok","q7":"fail"})
    operator: Optional[str] = "Counter_Default"
    cargo_type: CargoType = CargoType.GENERAL
    length: Optional[float] = 0
    width: Optional[float] = 0
    height: Optional[float] = 0
    weight_declared: Optional[float] = 0
    weight_real: Optional[float] = 0

class ValidationResult(BaseModel):
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
    chargeable_weight: float
    verified_weight: float
    weight_adjustment: float

# =========================
# PREGUNTAS BASE
# =========================

QUESTIONS_DB = [
    {"id":"q1","category":"DOCS","description":"MAWB original legible + 3 copias","tip":"Documento base","authority":"CBP / Avianca"},
    {"id":"q2","category":"DOCS","description":"HMAWB y Manifiesto coinciden 100%","tip":"Discrepancias generan multas","authority":"CBP AMS"},
    {"id":"q3","category":"DOCS","description":"Factura Comercial y Packing List","tip":"Indispensable para aduana","authority":"IATA"},
    {"id":"q4","category":"CBP","description":"EIN / Tax ID de Shipper y Consignee","tip":"Obligatorio para AMS","authority":"CBP"},
    {"id":"q5","category":"SECURITY","description":"Sello de camión intacto","tip":"Garantiza cadena de custodia","authority":"Chain of Custody"},
    {"id":"q6","category":"DIMENSIONS","description":"Altura ≤ 80cm (PAX) o ≤ 160cm (Carguero)","tip":"Exceder altura impide embarque","authority":"Engineering"}
]

# =========================
# UTILIDADES
# =========================

def generate_report_id() -> str:
    return f"SCR-{uuid.uuid4().hex[:8].upper()}"

def get_legal_disclaimer() -> str:
    return (
        "Este informe se emite bajo estándares IATA, CBP, TSA y DOT. "
        "SMARTCARGO BY MAY ROGA LLC valida previamente la carga para proteger el avión, aumentar rentabilidad y reducir riesgos."
    )

# =========================
# SMARTCARGO LOGIC
# =========================

class SmartCargoAdvisory:
    def __init__(self, data: CargoAnswer):
        self.data = data
        self.errors = []
        self.recommendations = []
        self.status = AlertLevel.GREEN
        self.chargeable_weight = 0
        self.verified_weight = 0
        self.weight_adjustment = 0

    def calculate_metrics(self):
        l = float(self.data.length or 0)
        w = float(self.data.width or 0)
        h = float(self.data.height or 0)
        weight_declared = float(self.data.weight_declared or 0)
        weight_real = float(self.data.weight_real or 0)

        # Peso Volumétrico
        vol_weight = (l * w * h) / 6000
        self.chargeable_weight = max(weight_real, vol_weight)
        self.verified_weight = weight_real
        self.weight_adjustment = round(self.chargeable_weight - weight_declared,2)

        # Presión sobre Piso (Floor Load)
        area_m2 = (l / 100) * (w / 100)
        floor_load = weight_real / area_m2 if area_m2 > 0 else 0

        # Alertas por presión
        if floor_load <= 732:
            self.recommendations.append("Carga segura, proceder normalmente.")
        elif floor_load <= 1000:
            self.recommendations.append("ALERTA: Presión alta. Aplicar SHORING (tablas distribuidoras).")
            self.status = AlertLevel.YELLOW
        else:
            self.recommendations.append("RIESGO ESTRUCTURAL: No recibir sin aprobación de Ingeniería de Vuelo.")
            self.status = AlertLevel.RED

        # Validaciones adicionales
        if h > 80 and self.data.cargo_type == CargoType.GENERAL:
            self.errors.append("Altura excede límite PAX, transferir a carguero o rechazar ingreso.")
            self.status = AlertLevel.RED

        if weight_real > weight_declared * 1.02:
            self.errors.append(f"Discrepancia: Peso real > 2% del declarado, ajustar tarifa por {weight_real - weight_declared} kg.")
            if self.status == AlertLevel.GREEN:
                self.status = AlertLevel.YELLOW

    def get_report(self):
        self.calculate_metrics()
        return ValidationResult(
            report_id=generate_report_id(),
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            operator=self.data.operator or "Counter_Default",
            cargo_type=self.data.cargo_type.value,
            total_questions=len(QUESTIONS_DB),
            green=len([1 for v in self.data.answers.values() if v=="ok"]),
            yellow=len([1 for v in self.data.answers.values() if v=="warn"]),
            red=len([1 for v in self.data.answers.values() if v=="fail"]),
            status=self.status,
            recommendations=self.recommendations + self.errors,
            legal_note=get_legal_disclaimer(),
            chargeable_weight=self.chargeable_weight,
            verified_weight=self.verified_weight,
            weight_adjustment=self.weight_adjustment
        )
