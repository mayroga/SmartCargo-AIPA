# models.py
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
import uuid

# =========================
# ENUMS (ESTÁNDARES DE CARGA)
# =========================

class Role(str, Enum):
    OWNER = "Owner"
    TRUCKER = "Trucker"
    FORWARDER = "Forwarder"
    COUNTER = "Counter"
    DG = "DG"
    HUMAN_REMAINS = "Human Remains"


class AlertLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


# =========================
# ESTRUCTURAS DE DATOS CORE
# =========================

class Question:
    def __init__(
        self,
        id: str,
        text: str,
        role: Role,
        red_if: Optional[str] = None,
        yellow_if: Optional[str] = None,
        reference: Optional[str] = None
    ):
        self.id = id
        self.text = text
        self.role = role
        self.red_if = red_if
        self.yellow_if = yellow_if
        self.reference = reference


class Answer:
    def __init__(self, question_id: str, value: str):
        self.question_id = question_id
        # Mapeo de valores de HTML a AlertLevel
        if value == "ok":
            self.level = AlertLevel.GREEN
        elif value == "warn":
            self.level = AlertLevel.YELLOW
        else:
            self.level = AlertLevel.RED


class Dimensions:
    def __init__(self, height_cm: float, width_cm: float, length_cm: float, weight_kg: float):
        self.height_cm = height_cm
        self.width_cm = width_cm
        self.length_cm = length_cm
        self.weight_kg = weight_kg

    @property
    def volume_cbm(self) -> float:
        return round((self.height_cm * self.width_cm * self.length_cm) / 1_000_000, 3)


class CargoReport:
    def __init__(
        self,
        operator: str,
        answers: List[Answer],
        dimensions: Optional[Dimensions] = None
    ):
        self.report_id = f"SCR-{uuid.uuid4().hex[:8].upper()}"
        self.operator = operator
        self.answers = answers
        self.dimensions = dimensions
        self.created_at = datetime.utcnow()

    def calculate_semaphore(self) -> AlertLevel:
        # Si hay un solo ROJO, el estatus es RED
        if any(a.level == AlertLevel.RED for a in self.answers):
            return AlertLevel.RED
        # Si hay amarillos pero no rojos, es YELLOW
        if any(a.level == AlertLevel.YELLOW for a in self.answers):
            return AlertLevel.YELLOW
        return AlertLevel.GREEN

    def count_by_color(self) -> Dict[str, int]:
        return {
            "green": sum(1 for a in self.answers if a.level == AlertLevel.GREEN),
            "yellow": sum(1 for a in self.answers if a.level == AlertLevel.YELLOW),
            "red": sum(1 for a in self.answers if a.level == AlertLevel.RED)
        }


# =========================
# LÍMITES DE DIMENSIONES AVIANCA
# =========================

AVIATION_LIMITS = {
    "PAX_NARROW_BODY": {
        "max_height_cm": 80,
        "max_width_cm": 120,
        "max_length_cm": 120,
        "aircraft": ["A319", "A320", "A321"],
        "rule": "Piezas > 80cm de altura no son aptas para aviones de pasajeros."
    },
    "FREIGHTER_A330F": {
        "main_deck_height_cm": 244,
        "lower_deck_height_cm": 162,
        "max_piece_length_cm": 300,
        "rule": "Piezas que excedan 300cm requieren aprobación técnica."
    }
}


# =========================
# DATA SET DE 49 PREGUNTAS (SMARTCARGO)
# =========================

# Esta lista sirve como referencia para el motor de asesoría
QUESTIONS_REF: List[Question] = [
    # Propietario / Cliente (1-8)
    Question("q1", "AWB original legible", Role.OWNER),
    Question("q2", "Factura y packing list completos", Role.OWNER),
    Question("q3", "Declaración coincide con documentos", Role.OWNER),
    Question("q4", "Permisos y certificados presentes", Role.OWNER),
    Question("q5", "Peso declarado coincide con carga", Role.OWNER),
    Question("q6", "Tipo de carga declarada en papel", Role.OWNER),
    Question("q7", "Shipper coincide con AWB", Role.OWNER),
    Question("q8", "Docs Human Remains completos", Role.OWNER),
    
    # Chofer / Camión (9-14)
    Question("q9", "Camión refrigerado adecuado", Role.TRUCKER),
    Question("q10", "Camión limpio y seguro", Role.TRUCKER),
    Question("q11", "Sello del camión presente", Role.TRUCKER),
    Question("q12", "Carga asegurada y estable", Role.TRUCKER),
    Question("q13", "Temperatura registrada correctamente", Role.TRUCKER),
    Question("q14", "Pallet y embalaje adecuado", Role.TRUCKER),

    # Forwarder (15-21)
    Question("q15", "AWB coincidente con documentos", Role.FORWARDER),
    Question("q16", "House / Master AWB alineados", Role.FORWARDER),
    Question("q17", "Packaging revisado y aprobado", Role.FORWARDER),
    Question("q18", "Temperatura declarada compatible", Role.FORWARDER),
    Question("q19", "Dry Ice declarado y etiquetado", Role.FORWARDER),
    Question("q20", "Fragile declarado y embalaje", Role.FORWARDER),
    Question("q21", "Docs Human Remains completos", Role.FORWARDER),

    # Counter (22-28)
    Question("q22", "Altura dentro de límite Avianca", Role.COUNTER),
    Question("q23", "Largo y ancho dentro de límite", Role.COUNTER),
    Question("q24", "Peso por pie cuadrado seguro", Role.COUNTER),
    Question("q25", "Carga estable y segura", Role.COUNTER),
    Question("q26", "No mezcla DG/Pharma/Perecedero", Role.COUNTER),
    Question("q27", "Etiquetas visibles y legibles", Role.COUNTER),
    Question("q28", "Verificación docs completa", Role.COUNTER),

    # Mercancías Peligrosas (29-34)
    Question("q29", "DG declarado en AWB", Role.DG),
    Question("q30", "Clase DG correcta", Role.DG),
    Question("q31", "DGD y MSDS firmados", Role.DG),
    Question("q32", "Embalaje UN aprobado", Role.DG),
    Question("q33", "Labels DG visibles", Role.DG),
    Question("q34", "DG no mezclado", Role.DG),

    # Human Remains & Especiales (35-49)
    Question("q35", "Ataúd conforme y embalaje", Role.HUMAN_REMAINS),
    Question("q36", "Packing list separado", Role.HUMAN_REMAINS),
    Question("q37", "Docs Human Remains correctos", Role.HUMAN_REMAINS),
    Question("q38", "Tiempo tránsito compatible", Role.HUMAN_REMAINS),
    Question("q39", "Temperatura y ventilación", Role.HUMAN_REMAINS),
    Question("q40", "Peso total validado", Role.HUMAN_REMAINS),
    Question("q41", "Facturas y packing organizados", Role.HUMAN_REMAINS),
    Question("q42", "Peso coincidente documentos", Role.HUMAN_REMAINS),
    Question("q43", "Docs consolidados correctos", Role.HUMAN_REMAINS),
    Question("q44", "Apto belly cargo", Role.HUMAN_REMAINS),
    Question("q45", "No mezcla DG / Perecedero", Role.HUMAN_REMAINS),
    Question("q46", "Checklist completo revisado", Role.HUMAN_REMAINS),
    Question("q47", "Peso bulto y pallets verificado", Role.HUMAN_REMAINS),
    Question("q48", "Revisión final semáforo", Role.HUMAN_REMAINS),
    Question("q49", "Recomendaciones claras", Role.HUMAN_REMAINS),
]
