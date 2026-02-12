# models.py
from typing import List, Optional
from enum import Enum
from datetime import datetime


# =========================
# ENUMS
# =========================

class Role(str, Enum):
    OWNER = "Owner"
    TRUCKER = "Trucker"
    FORWARDER = "Forwarder"
    COUNTER = "Counter"
    DG = "DG"


class AlertLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


# =========================
# CORE DATA STRUCTURES
# =========================

class Question:
    def __init__(
        self,
        id: int,
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
    def __init__(self, question_id: int, value: AlertLevel):
        self.question_id = question_id
        self.value = value


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
        role: Role,
        answers: List[Answer],
        dimensions: Dimensions
    ):
        self.operator = operator
        self.role = role
        self.answers = answers
        self.dimensions = dimensions
        self.created_at = datetime.utcnow()

    def calculate_semaphore(self) -> AlertLevel:
        for a in self.answers:
            if a.value == AlertLevel.RED:
                return AlertLevel.RED
        for a in self.answers:
            if a.value == AlertLevel.YELLOW:
                return AlertLevel.YELLOW
        return AlertLevel.GREEN

    def count_by_color(self):
        green = sum(1 for a in self.answers if a.value == AlertLevel.GREEN)
        yellow = sum(1 for a in self.answers if a.value == AlertLevel.YELLOW)
        red = sum(1 for a in self.answers if a.value == AlertLevel.RED)
        return green, yellow, red


# =========================
# AVIanca DIMENSION LIMITS
# =========================

AVIATION_LIMITS = {
    "PAX": {
        "max_height_cm": 80,
        "max_width_cm": 120,
        "max_length_cm": 120,
        "aircraft": ["A319", "A320", "A321"],
        "rule": "Si excede 80 cm de alto → RECHAZO AUTOMÁTICO"
    },
    "CARGO_A330F": {
        "main_deck_height_cm": 244,
        "lower_deck_height_cm": 162,
        "max_piece_length_cm": 300,
        "rule": "Piezas >300 cm requieren aprobación de ingeniería"
    }
}


# =========================
# FINAL QUESTION SET (49)
# =========================

QUESTIONS: List[Question] = [

    # ---------- IDENTIFICATION ----------
    Question(1, "Tipo de carga correctamente declarada", Role.OWNER,
             red_if="Tipo incorrecto", reference="IATA AHM"),
    Question(2, "Shipper / Owner identificado", Role.OWNER,
             red_if="No identificado"),
    Question(3, "Documentos entregados completos", Role.OWNER,
             yellow_if="Faltan copias"),

    # ---------- TRUCK / DELIVERY ----------
    Question(4, "Camión adecuado para el tipo de carga", Role.TRUCKER,
             red_if="Camión no apto"),
    Question(5, "Carga protegida durante transporte", Role.TRUCKER,
             yellow_if="Protección parcial"),
    Question(6, "Camión limpio y sin contaminación", Role.TRUCKER,
             red_if="Camión contaminado"),
    Question(7, "Sello del camión presente", Role.TRUCKER,
             red_if="Sin sello"),
    Question(8, "Temperatura controlada (si aplica)", Role.TRUCKER,
             red_if="Fuera de rango"),

    # ---------- DIMENSIONS ----------
    Question(9, "Altura compatible con aeronave asignada", Role.COUNTER,
             red_if="Excede límites Avianca"),
    Question(10, "Largo compatible con tipo de avión", Role.COUNTER,
              red_if="Excede 300 cm"),
    Question(11, "Peso distribuido correctamente", Role.COUNTER,
              yellow_if="Requiere shoring"),

    # ---------- DOCUMENTATION ----------
    Question(12, "AWB original presente", Role.FORWARDER,
              red_if="No disponible"),
    Question(13, "AWB legible y sin enmiendas", Role.FORWARDER,
              yellow_if="Correcciones visibles"),
    Question(14, "House y Master AWB coinciden", Role.FORWARDER,
              red_if="Inconsistencia"),
    Question(15, "Factura comercial correcta", Role.FORWARDER,
              red_if="Datos incorrectos"),
    Question(16, "Packing List coincide con carga", Role.FORWARDER,
              red_if="No coincide"),
    Question(17, "Permisos y certificados completos", Role.FORWARDER,
              yellow_if="Faltan anexos"),

    # ---------- PALLETS ----------
    Question(18, "Pallet aprobado para aviación", Role.COUNTER,
              red_if="Pallet no permitido"),
    Question(19, "Carga correctamente envuelta", Role.COUNTER,
              yellow_if="Envoltura deficiente"),
    Question(20, "Etiquetas visibles", Role.COUNTER,
              yellow_if="No visibles"),
    Question(21, "Carga segregada correctamente", Role.COUNTER,
              red_if="Mezcla no permitida"),

    # ---------- PHARMA ----------
    Question(22, "Carga farmacéutica declarada", Role.FORWARDER),
    Question(23, "Rango de temperatura indicado", Role.FORWARDER,
              red_if="No declarado"),
    Question(24, "Dispositivos térmicos presentes", Role.COUNTER,
              yellow_if="Cantidad insuficiente"),

    # ---------- DG ----------
    Question(25, "Mercancía peligrosa declarada", Role.DG,
              red_if="DG no declarada"),
    Question(26, "Clase DG correcta", Role.DG,
              red_if="Clase incorrecta"),
    Question(27, "DGD firmada", Role.DG,
              red_if="No firmada"),
    Question(28, "MSDS adjunto", Role.DG,
              red_if="No disponible"),
    Question(29, "Embalaje UN aprobado", Role.DG,
              red_if="No conforme"),
    Question(30, "Etiquetas DG visibles", Role.DG,
              red_if="Faltantes"),

    # ---------- PERISHABLE ----------
    Question(31, "Tipo perecedero identificado", Role.FORWARDER),
    Question(32, "Tiempo de tránsito compatible", Role.FORWARDER,
              yellow_if="Margen crítico"),
    Question(33, "Ventilación adecuada", Role.COUNTER,
              red_if="No adecuada"),

    # ---------- HUMAN REMAINS ----------
    Question(34, "Documentos Human Remains completos", Role.FORWARDER,
              red_if="Faltantes"),
    Question(35, "Ataúd conforme normativa", Role.COUNTER,
              red_if="No conforme"),
    Question(36, "AWB HR correcta", Role.COUNTER,
              red_if="Error en AWB"),

    # ---------- FINAL ----------
    Question(37, "Peso coincide con documentación", Role.COUNTER,
              red_if="Diferencia"),
    Question(38, "Volumen dentro de límites", Role.COUNTER,
              red_if="Excede"),
    Question(39, "Carga apta para Belly Cargo", Role.COUNTER,
              red_if="No apta"),
    Question(40, "No mezcla DG/PER", Role.COUNTER,
              red_if="Mezcla crítica"),
    Question(41, "Checklist completo", Role.COUNTER,
              yellow_if="Incompleto"),
    Question(42, "Aprobación supervisor requerida", Role.COUNTER),
    Question(43, "Carga lista para build-up", Role.COUNTER),
    Question(44, "Cumple IATA", Role.COUNTER,
              red_if="Incumplimiento"),
    Question(45, "Cumple DOT", Role.COUNTER,
              red_if="Incumplimiento"),
    Question(46, "Cumple CBP", Role.COUNTER,
              red_if="Incumplimiento"),
    Question(47, "Cumple estándar Avianca", Role.COUNTER,
              red_if="No conforme"),
    Question(48, "No requiere corrección adicional", Role.COUNTER),
    Question(49, "Autorizado para embarque", Role.COUNTER)
]
