from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import uuid

from models import (
    CargoAnswer,
    ValidationResult,
    AlertLevel,
    CargoType,
    QUESTIONS_DB,
    get_questions_by_type,
    generate_report_id,
    get_legal_disclaimer
)

app = FastAPI(title="SMARTCARGO BY MAY ROGA LLC", version="3.0")

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# FRONTEND INTEGRADO
# =========================
HTML_CONTENT = open("frontend/index.html", "r", encoding="utf-8").read()

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_CONTENT

# =========================
# API PARA PREGUNTAS
# =========================
@app.get("/get_questions/{cargo_type}")
def api_get_questions(cargo_type: str):
    try:
        cargo_enum = CargoType[cargo_type]
    except KeyError:
        raise HTTPException(status_code=400, detail="Tipo de carga inválido")
    questions = get_questions_by_type(cargo_enum)
    return questions

# =========================
# API PARA VALIDACIÓN
# =========================
class CargoAnswerRequest(BaseModel):
    cargo_type: str
    answers: Dict[str, str]
    operator: str = "Counter_Default"

@app.post("/validate_cargo")
def validate_cargo(data: CargoAnswerRequest):
    cargo_enum = CargoType[data.cargo_type] if data.cargo_type in CargoType.__members__ else CargoType.GENERAL
    questions = get_questions_by_type(cargo_enum)

    green = yellow = red = 0
    recommendations = []

    for q in questions:
        qid = q["id"]
        ans = data.answers.get(qid, "RED")  # default = RED si no responde
        desc = q["description"]

        if ans.upper() == "GREEN":
            green += 1
        elif ans.upper() == "YELLOW":
            yellow += 1
            recommendations.append(f"OBSERVACIÓN en {qid}: {desc}")
        else:
            red += 1
            recommendations.append(f"RECHAZO CRÍTICO en {qid}: {desc}")

    # Determinar nivel de alerta global
    if red > 0:
        status = AlertLevel.RED
        recommendations.insert(0, "DICTAMEN: CARGA NO APTA. Incumplimiento de seguridad.")
    elif yellow > 0:
        status = AlertLevel.YELLOW
        recommendations.insert(0, "DICTAMEN: ACEPTACIÓN CONDICIONADA. Verificar observaciones.")
    else:
        status = AlertLevel.GREEN
        recommendations.insert(0, "DICTAMEN: CUMPLIMIENTO TOTAL. Proceder con el embarque.")

    result = ValidationResult(
        report_id=generate_report_id(),
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        operator=data.operator,
        cargo_type=cargo_enum.value,
        total_questions=len(questions),
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recommendations,
        legal_note=get_legal_disclaimer()
    )

    return result

# =========================
# RUN INSTRUCTIONS
# =========================
# uvicorn main:app --reload
