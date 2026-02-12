# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import uuid

from models import build_levels, CargoReport

app = FastAPI(title="SMARTCARGO-AIPA", version="1.0")

# =========================
# STATIC & TEMPLATES
# =========================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="frontend")

# =========================
# DATA MODELS
# =========================
class CargoValidation(BaseModel):
    answers: dict  # {"q1":"ok","q2":"warn","q3":"fail",...}
    operator: str | None = "Unknown"

class ValidationResult(BaseModel):
    report_id: str
    timestamp: str
    operator: str
    total_questions: int
    green: int
    yellow: int
    red: int
    status: str
    recommendations: list[str]

# =========================
# ROUTES
# =========================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/validate", response_model=ValidationResult)
async def validate_cargo(data: CargoValidation):

    # Construimos los niveles y preguntas
    levels = build_levels()
    report = CargoReport(report_id=f"SCR-{uuid.uuid4().hex[:8].upper()}", role=data.operator, levels=levels)

    # =========================
    # MAPEAR RESPUESTAS DEL FRONTEND
    # =========================
    q_counter = 1
    for lvl in report.levels:
        for q in lvl.questions:
            key = f"q{q_counter}"
            if key in data.answers:
                val = data.answers[key]
                if val == "ok":
                    q.selected = "ok"
                    q.alert = ""  # Cumple
                elif val == "warn":
                    q.selected = "warn"
                    q.alert = "AMARILLA"
                elif val == "fail":
                    q.selected = "fail"
                    q.alert = "ROJA"
            q_counter += 1

    # =========================
    # CALCULO DE SEMAFORO
    # =========================
    status = report.calculate_semaforo()
    red = sum(q.alert == "ROJA" for lvl in report.levels for q in lvl.questions)
    yellow = sum(q.alert == "AMARILLA" for lvl in report.levels for q in lvl.questions)
    green = sum(q.alert == "" for lvl in report.levels for q in lvl.questions)
    total_questions = red + yellow + green

    # =========================
    # GENERACION DE RECOMENDACIONES
    # =========================
    recommendations = report.generate_recommendations()

    # Mensajes generales SMARTCARGO-AIPA según semáforo
    if status == "GREEN":
        recommendations.insert(0, "✅ Cargo aceptado para procesamiento.")
        recommendations.insert(1, "Proceder con build-up y planificación de vuelo.")
    elif status == "YELLOW":
        recommendations.insert(0, "⚠ Cargo condicionalmente aceptado, revisión necesaria por supervisor.")
        recommendations.insert(1, "Verificar documentación, etiquetado, temperatura y segregación.")
    elif status == "RED":
        recommendations.insert(0, "❌ Cargo NO aceptado, acción correctiva inmediata requerida.")
        recommendations.insert(1, "Aislar carga y notificar supervisor antes de continuar.")
        recommendations.insert(2, "No proceder hasta que todos los problemas críticos sean resueltos.")

    # ADICIONAL: alertas por volumen de fallas
    if red >= 3:
        recommendations.append("⚠ Múltiples fallas críticas detectadas – escalar a gerencia.")
    if yellow >= 5:
        recommendations.append("⚠ Alto volumen de alertas – realizar inspección secundaria completa.")

    # =========================
    # RESPUESTA FINAL
    # =========================
    return ValidationResult(
        report_id=report.report_id,
        timestamp=datetime.utcnow().isoformat(),
        operator=data.operator,
        total_questions=total_questions,
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recommendations
    )

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "OK", "system": "SMARTCARGO-AIPA"}
