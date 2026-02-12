from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Dict, List

app = FastAPI(
    title="SMARTCARGO-AIPA",
    version="2.0",
    description="Operational Cargo Pre-Validation System"
)

# ===============================
# STATIC FRONTEND
# ===============================
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
def load_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

# ===============================
# DATA MODELS
# ===============================
class Answer(BaseModel):
    question_id: int
    value: str  # green | yellow | red
    role: str

class ValidationPayload(BaseModel):
    operator: str
    role: str
    answers: List[Answer]
    dimensions: Dict[str, float] | None = None  # height, width, length, weight

class ValidationResult(BaseModel):
    report_id: str
    timestamp: str
    operator: str
    final_status: str
    counts: Dict[str, int]
    actions: List[str]

# ===============================
# CORE VALIDATION
# ===============================
@app.post("/validate", response_model=ValidationResult)
def validate_cargo(payload: ValidationPayload):

    green = yellow = red = 0

    for ans in payload.answers:
        if ans.value == "green":
            green += 1
        elif ans.value == "yellow":
            yellow += 1
        elif ans.value == "red":
            red += 1

    # ===============================
    # SEMÁFORO OPERATIVO
    # ===============================
    if red > 0:
        final_status = "RED"
    elif yellow > 0:
        final_status = "YELLOW"
    else:
        final_status = "GREEN"

    actions = generate_actions(
        final_status=final_status,
        payload=payload,
        red=red,
        yellow=yellow
    )

    return ValidationResult(
        report_id=f"AIPA-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow().isoformat(),
        operator=payload.operator,
        final_status=final_status,
        counts={
            "green": green,
            "yellow": yellow,
            "red": red,
            "total": len(payload.answers)
        },
        actions=actions
    )

# ===============================
# BUSINESS LOGIC (AVIATION REAL)
# ===============================
def generate_actions(final_status: str, payload: ValidationPayload, red: int, yellow: int) -> List[str]:
    actions = []

    if final_status == "GREEN":
        actions.append("🟢 Carga aprobada para recepción en Avianca Cargo.")
        actions.append("Proceder a aceptación en counter.")
        actions.append("Registrar evidencia y continuar flujo normal.")

    if final_status == "YELLOW":
        actions.append("🟡 Carga con observaciones.")
        actions.append("Revisión obligatoria antes de embarque.")
        actions.append("Counter debe verificar documentación y medidas.")
        actions.append("Supervisor recomendado.")

    if final_status == "RED":
        actions.append("🔴 CARGA RECHAZADA.")
        actions.append("NO aceptar en counter.")
        actions.append("Aislar la carga.")
        actions.append("Notificar inmediatamente a:")
        actions.append("- Freight Forwarder")
        actions.append("- Agente DG (si aplica)")
        actions.append("- Supervisor de Operaciones")

    # ===============================
    # DIMENSIONES AVIATION
    # ===============================
    dims = payload.dimensions
    if dims:
        h = dims.get("height", 0)
        w = dims.get("width", 0)
        l = dims.get("length", 0)

        volume = round((h * w * l) / 1_000_000, 3)
        actions.append(f"📦 Volumen calculado: {volume} m³")

        if h > 80:
            actions.append("❌ Altura excede límite PAX (80 cm). Reubicar a carguero.")
        if h > 244:
            actions.append("❌ Altura excede Main Deck A330F. Rechazo técnico.")
        if l > 300:
            actions.append("⚠️ Carga larga. Requiere aprobación de Ingeniería.")

    # ===============================
    # ESCALATION RULES
    # ===============================
    if red >= 3:
        actions.append("🚨 Fallas críticas múltiples. Escalamiento obligatorio a gerencia.")
    if yellow >= 5:
        actions.append("⚠️ Alto número de observaciones. Inspección secundaria completa.")

    return actions

# ===============================
# HEALTH CHECK
# ===============================
@app.get("/health")
def health():
    return {
        "status": "OK",
        "system": "SMARTCARGO-AIPA",
        "mode": "Operational",
        "timestamp": datetime.utcnow().isoformat()
    }
