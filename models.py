from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import uuid

# =========================
# ENUMS PRINCIPALES
# =========================

class CargoType(str, Enum):
    GENERAL = "General Cargo"
    DG = "Dangerous Goods"
    PERISHABLE = "Perishable"
    LIVE_ANIMALS = "Live Animals"
    EXPRESS = "Express Cargo"
    PASSENGER_BAGGAGE = "Passenger Baggage"
    MAIL = "Mail"
    COMAT = "COMAT (Company Material)"

class AlertLevel(str, Enum):
    GREEN = "APTO"
    YELLOW = "OBSERVACIÓN"
    RED = "RECHAZO"

# =========================
# MODELOS DE DATOS
# =========================

class CargoAnswer:
    """
    Estructura para recibir respuestas de la interfaz.
    """
    answers: Dict[str, str]  # {question_id: "ok"|"warn"|"fail"}
    operator: Optional[str] = "Counter_Default"
    cargo_type: CargoType = CargoType.GENERAL

class ValidationResult:
    """
    Estructura de respuesta tras validar la carga.
    """
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
# FUNCIONES DE UTILIDAD
# =========================

def generate_report_id() -> str:
    return str(uuid.uuid4()).split('-')[0].upper()

def get_legal_disclaimer() -> str:
    return (
        "SMARTCARGO BY MAY ROGA LLC proporciona recomendaciones basadas en regulaciones IATA, "
        "CBP, DOT y TSA. No sustituye inspecciones físicas obligatorias ni responsabilidades legales de la aerolínea."
    )

# =========================
# BASE DE PREGUNTAS (40+)
# =========================

QUESTIONS_DB = [
    # 1-10: DOCUMENTACIÓN Y AWB
    {"id": "q01", "description": "AWB correctamente emitida con número de vuelo y fecha.", "tip": "IATA 6.1.1", "authority": "IATA"},
    {"id": "q02", "description": "Declaración de valor y seguro presentes.", "tip": "IATA 8.4", "authority": "IATA"},
    {"id": "q03", "description": "Manifestación correcta según CBP.", "tip": "CBP 19 CFR", "authority": "CBP"},
    {"id": "q04", "description": "Documentos de exportación/importación según país.", "tip": "DOT / FAA", "authority": "DOT"},
    {"id": "q05", "description": "Etiqueta de origen y destino correcta.", "tip": "IATA 7.1", "authority": "IATA"},
    {"id": "q06", "description": "Número de tracking y referencia interna validada.", "tip": "Airline Standard", "authority": "Avianca"},
    {"id": "q07", "description": "Formulario de DG completado si aplica.", "tip": "IATA DGR 8.0", "authority": "IATA"},
    {"id": "q08", "description": "Permisos especiales para carga especial (médica, armas, organismos vivos).", "tip": "CBP / TSA", "authority": "CBP"},
    {"id": "q09", "description": "Declaración de contenido y cantidad precisa.", "tip": "IATA 7.2", "authority": "IATA"},
    {"id": "q10", "description": "Inspección previa de documentos firmada por el operador.", "tip": "Airline SOP", "authority": "Avianca"},

    # 11-20: SEGURIDAD Y PESO
    {"id": "q11", "description": "Peso total no excede límite de vuelo.", "tip": "DOT / IATA 6.7", "authority": "IATA"},
    {"id": "q12", "description": "Distribución del peso equilibrada en ULD o palet.", "tip": "IATA 6.7.2", "authority": "IATA"},
    {"id": "q13", "description": "Cargas peligrosas correctamente separadas.", "tip": "IATA DGR", "authority": "IATA"},
    {"id": "q14", "description": "Presión de piso compatible con tipo de ULD.", "tip": "Avianca Cargo SOP", "authority": "Avianca"},
    {"id": "q15", "description": "Shoring o refuerzo utilizado si necesario.", "tip": "IATA 6.7.3", "authority": "IATA"},
    {"id": "q16", "description": "Cargas refrigeradas con temperatura monitoreada.", "tip": "IATA CEIV Pharma", "authority": "IATA"},
    {"id": "q17", "description": "Live animals asegurados y ventilados.", "tip": "IATA Live Animals", "authority": "IATA"},
    {"id": "q18", "description": "Peso volumétrico correctamente calculado.", "tip": "IATA 6.7", "authority": "IATA"},
    {"id": "q19", "description": "Carga sobrepasada en altura o volumen revisada.", "tip": "Avianca SOP", "authority": "Avianca"},
    {"id": "q20", "description": "Unidad de carga asegurada con straps o net.", "tip": "IATA 6.8", "authority": "IATA"},

    # 21-30: RESTRICCIONES Y DG
    {"id": "q21", "description": "No hay explosivos o materiales prohibidos.", "tip": "IATA DGR 2.0", "authority": "IATA"},
    {"id": "q22", "description": "Baterías de litio embaladas y etiquetadas correctamente.", "tip": "IATA DGR 4.2", "authority": "IATA"},
    {"id": "q23", "description": "Sustancias químicas clasificadas y separadas.", "tip": "IATA DGR 3.0", "authority": "IATA"},
    {"id": "q24", "description": "Marcaje de DG visible y no dañado.", "tip": "IATA DGR 7.0", "authority": "IATA"},
    {"id": "q25", "description": "Cantidad máxima por ULD respetada.", "tip": "IATA DGR 1.0", "authority": "IATA"},
    {"id": "q26", "description": "Artículos de riesgo biológico identificados.", "tip": "IATA DGR 6.0", "authority": "IATA"},
    {"id": "q27", "description": "Carga con medicamentos cumple CEIV Pharma.", "tip": "IATA CEIV", "authority": "IATA"},
    {"id": "q28", "description": "Carga express etiquetada con prioridad correcta.", "tip": "Airline SOP", "authority": "Avianca Express"},
    {"id": "q29", "description": "Carga COMAT declarada y entregada por personal autorizado.", "tip": "Airline SOP", "authority": "Avianca COMAT"},
    {"id": "q30", "description": "Correo o paquetes postales con control aduanero.", "tip": "CBP / Postal Regulations", "authority": "CBP"},

    # 31-40: CLIENTES, PROCEDIMIENTOS Y ALERTAS
    {"id": "q31", "description": "Cliente correctamente registrado y autorizado.", "tip": "Airline SOP", "authority": "Avianca"},
    {"id": "q32", "description": "Facturación electrónica emitida según DOT.", "tip": "DOT 14 CFR", "authority": "DOT"},
    {"id": "q33", "description": "Alertas previas de peso o volumen revisadas.", "tip": "Airline SOP", "authority": "Avianca"},
    {"id": "q34", "description": "Procedimiento de check-in respetado para carga.", "tip": "IATA 7.0", "authority": "IATA"},
    {"id": "q35", "description": "Registro de inspección de seguridad firmado.", "tip": "Airline SOP", "authority": "Avianca"},
    {"id": "q36", "description": "Equipos especiales (gruas, rampas) disponibles.", "tip": "Airline SOP", "authority": "Avianca"},
    {"id": "q37", "description": "Discrepancias entre AWB y contenido verificadas.", "tip": "IATA 8.2", "authority": "IATA"},
    {"id": "q38", "description": "Cargas refrigeradas y perecederos etiquetadas y revisadas.", "tip": "IATA CEIV", "authority": "IATA"},
    {"id": "q39", "description": "Cargas de alto valor aseguradas y documentadas.", "tip": "Airline SOP", "authority": "Avianca"},
    {"id": "q40", "description": "Todos los procedimientos cumplen con normas internas de Avianca Cargo.", "tip": "Airline SOP", "authority": "Avianca"},
]

# =========================
# EXTENSIÓN: FUNCIONES PARA FUTURO CRECIMIENTO
# =========================

def get_questions_by_type(cargo_type: CargoType) -> List[Dict]:
    """
    Filtra preguntas relevantes según tipo de carga.
    """
    if cargo_type == CargoType.DG:
        return [q for q in QUESTIONS_DB if "DG" in q["tip"] or "Dangerous" in q["description"]]
    elif cargo_type == CargoType.PERISHABLE or cargo_type == CargoType.LIVE_ANIMALS:
        return [q for q in QUESTIONS_DB if "Live Animals" in q["tip"] or "refrigerado" in q["description"].lower()]
    elif cargo_type == CargoType.EXPRESS:
        return [q for q in QUESTIONS_DB if "Express" in q["tip"] or "express" in q["description"].lower()]
    elif cargo_type == CargoType.COMAT:
        return [q for q in QUESTIONS_DB if "COMAT" in q["description"]]
    else:
        return QUESTIONS_DB
