from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import uuid

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
    answers: dict       # {"q1":"ok","q2":"warn","q3":"fail",...}
    operator: str | None = "Unknown"
    dimensions: dict | None = {}  # {"q5":{"height":80,"width":120,"length":120},...}
    ia_user: str | None = ""
    ia_pass: str | None = ""

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
    total_volume_cm3: float

# =========================
# ROUTES
# =========================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/validate", response_model=ValidationResult)
async def validate_cargo(data: CargoValidation):
    # =========================
    # Validación básica IA experta (solo ejemplo)
    # =========================
    if data.ia_user != "admin" or data.ia_pass != "password":
        raise HTTPException(status_code=401, detail="Invalid IA Expert credentials")

    total_questions = 35  # Número de preguntas definido en frontend/index.html
    green = yellow = red = 0

    # =========================
    # Contar respuestas por color
    # =========================
    for value in data.answers.values():
        if value == "ok":
            green += 1
        elif value == "warn":
            yellow += 1
        elif value == "fail":
            red += 1

    # =========================
    # Semáforo
    # =========================
    if red > 0:
        status = "RED"
    elif yellow > 0:
        status = "YELLOW"
    else:
        status = "GREEN"

    # =========================
    # Cálculo de volumen total (cm3)
    # =========================
    total_volume = 0
    if data.dimensions:
        for dim in data.dimensions.values():
            h = dim.get("height", 0)
            w = dim.get("width", 0)
            l = dim.get("length", 0)
            total_volume += h * w * l

    # =========================
    # Recomendaciones profesionales
    # =========================
    recommendations = generate_recommendations(
        status=status,
        red=red,
        yellow=yellow
    )

    return ValidationResult(
        report_id=f"SCR-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow().isoformat(),
        operator=data.operator,
        total_questions=total_questions,
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recommendations,
        total_volume_cm3=total_volume
    )

# =========================
# BUSINESS LOGIC
# =========================
def generate_recommendations(status: str, red: int, yellow: int) -> list[str]:
    recs = []

    if status == "GREEN":
        recs.extend([
            "Cargo accepted for processing.",
            "Proceed with build-up and flight planning.",
            "Maintain current compliance standards."
        ])

    elif status == "YELLOW":
        recs.extend([
            "Cargo conditionally accepted.",
            "Supervisor review required before release.",
            "Re-check documentation, labeling, temperature, and segregation."
        ])

    elif status == "RED":
        recs.extend([
            "Cargo NOT accepted.",
            "Immediate corrective action required.",
            "Isolate cargo and notify supervisor.",
            "Do not proceed until all critical issues are resolved.",
            "Document non-compliance per SMARTCARGO-AIPA protocol."
        ])

    if red >= 3:
        recs.append("Multiple critical failures detected – escalate to management.")
    if yellow >= 5:
        recs.append("High warning volume – perform full secondary inspection.")

    return recs

# =========================
# PDF & WhatsApp Placeholder Endpoints
# =========================
@app.get("/pdf/{report_id}")
def generate_pdf(report_id: str):
    return {"message": f"PDF generation for report {report_id} will be implemented."}

@app.get("/whatsapp/{report_id}")
def send_whatsapp(report_id: str):
    return {"message": f"WhatsApp sending for report {report_id} will be implemented."}

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "OK", "system": "SMARTCARGO-AIPA"}
