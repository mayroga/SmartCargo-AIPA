from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime
from uuid import uuid4

from models import (
    AlertLevel,
    CargoType,
    QUESTIONS_DB,
    get_questions_by_type,
    generate_report_id,
    get_legal_disclaimer
)

# ======================================================
# APP
# ======================================================
app = FastAPI(
    title="SMARTCARGO – Audit Ready Cargo Validation",
    version="4.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ======================================================
# FRONTEND
# ======================================================
HTML_CONTENT = open("frontend/index.html", "r", encoding="utf-8").read()

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_CONTENT

# ======================================================
# MODELOS AUDIT / IA
# ======================================================
class AuditLog(BaseModel):
    audit_id: str
    timestamp: str
    airline: str
    role: str
    cargo_type: str
    decision: str
    message: str
    applied_rules: Dict[str, str]

class AIObservation(BaseModel):
    observation: str
    risk_level: str

# ======================================================
# REQUEST PRINCIPAL
# ======================================================
class CargoRequest(BaseModel):
    cargo_type: str
    answers: Dict[str, str]
    role: str = "COUNTER"
    airline: str = "AVIANCA"
    temperature_c: Optional[float] = None
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None

# ======================================================
# VALIDACIONES BASE (CORE – NO AEROLÍNEA)
# ======================================================
def validate_identity(role: str) -> AlertLevel:
    return AlertLevel.GREEN if role else AlertLevel.RED

def validate_documents(answers: Dict[str, str]) -> AlertLevel:
    if any(v == "RED" for v in answers.values()):
        return AlertLevel.RED
    if any(v == "YELLOW" for v in answers.values()):
        return AlertLevel.YELLOW
    return AlertLevel.GREEN

def validate_physical_conditions(data: CargoRequest) -> AlertLevel:
    if data.weight_kg and data.volume_m3:
        density = data.weight_kg / max(data.volume_m3, 0.01)
        if density > 300:
            return AlertLevel.YELLOW
    return AlertLevel.GREEN

# ======================================================
# REGLAS AVIANA CARGO (AISLADAS)
# ======================================================
def avianca_rules(data: CargoRequest) -> AlertLevel:

    # Perecederos – temperatura
    if data.cargo_type == "PERISHABLE" and data.temperature_c is not None:
        if data.temperature_c > 8:
            return AlertLevel.YELLOW

    # COMAT – solo personal autorizado
    if data.cargo_type == "COMAT" and data.role != "SUPERVISOR":
        return AlertLevel.RED

    # DG – densidad sospechosa
    if data.cargo_type == "DG" and data.weight_kg and data.volume_m3:
        if (data.weight_kg / max(data.volume_m3, 0.01)) > 400:
            return AlertLevel.YELLOW

    # Express – prioridad
    if data.cargo_type == "EXPRESS":
        if any(v == "RED" for v in data.answers.values()):
            return AlertLevel.RED

    return AlertLevel.GREEN

def apply_airline_rules(data: CargoRequest) -> AlertLevel:
    if data.airline.upper() == "AVIANCA":
        return avianca_rules(data)
    return AlertLevel.GREEN

# ======================================================
# DECISIÓN FINAL (NO IA)
# ======================================================
def final_decision(results: List[AlertLevel]):
    if AlertLevel.RED in results:
        return AlertLevel.RED, "Carga NO APTA – incumplimiento crítico"
    if AlertLevel.YELLOW in results:
        return AlertLevel.YELLOW, "Carga APTA CON OBSERVACIONES"
    return AlertLevel.GREEN, "Carga APTA – cumplimiento total"

# ======================================================
# IA SOLO OBSERVACIONES (NO DECIDE)
# ======================================================
def ai_observation_layer(data: CargoRequest) -> Optional[AIObservation]:
    notes = []

    if data.cargo_type == "PERISHABLE" and data.temperature_c:
        if data.temperature_c > 8:
            notes.append("Posible degradación térmica del producto")

    if data.weight_kg and data.volume_m3:
        if (data.weight_kg / max(data.volume_m3, 0.01)) > 250:
            notes.append("Alta densidad: posible inspección adicional")

    if not notes:
        return None

    return AIObservation(
        observation=" | ".join(notes),
        risk_level="INFORMATIVO"
    )

# ======================================================
# AUDIT LOG
# ======================================================
def generate_audit_log(
    data: CargoRequest,
    decision: AlertLevel,
    message: str,
    rules: Dict[str, str]
) -> AuditLog:
    return AuditLog(
        audit_id=str(uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        airline=data.airline,
        role=data.role,
        cargo_type=data.cargo_type,
        decision=decision.value,
        message=message,
        applied_rules=rules
    )

# ======================================================
# API PREGUNTAS
# ======================================================
@app.get("/get_questions/{cargo_type}")
def get_questions(cargo_type: str):
    try:
        cargo_enum = CargoType[cargo_type]
    except KeyError:
        raise HTTPException(status_code=400, detail="Tipo de carga inválido")
    return get_questions_by_type(cargo_enum)

# ======================================================
# ENDPOINT FINAL PRO
# ======================================================
@app.post("/validate-cargo")
def validate_cargo(data: CargoRequest):

    rules_applied = {}
    checks = []

    checks.append(validate_identity(data.role))
    rules_applied["identity"] = "validated"

    checks.append(validate_documents(data.answers))
    rules_applied["documents"] = "checked"

    checks.append(validate_physical_conditions(data))
    rules_applied["physical_conditions"] = "evaluated"

    airline_result = apply_airline_rules(data)
    checks.append(airline_result)
    rules_applied["avianca_rules"] = "applied"

    decision, message = final_decision(checks)

    audit_log = generate_audit_log(
        data=data,
        decision=decision,
        message=message,
        rules=rules_applied
    )

    ai_notes = ai_observation_layer(data)

    return {
        "decision": decision.value,
        "message": message,
        "audit_log": audit_log,
        "ai_observation": ai_notes,
        "legal_note": get_legal_disclaimer()
    }

# ======================================================
# RUN
# ======================================================
# uvicorn main:app --reload
