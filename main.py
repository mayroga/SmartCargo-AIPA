from fastapi import FastAPI, Request
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
templates = Jinja2Templates(directory="templates")

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
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/validate", response_model=ValidationResult)
async def validate_cargo(data: CargoValidation):

    total_questions = 49
    green = yellow = red = 0

    for qid, value in data.answers.items():
        if value == "ok":
            green += 1
        elif value == "warn":
            yellow += 1
        elif value == "fail":
            red += 1

    # =========================
    # SEMAPHORE LOGIC
    # =========================
    if red > 0:
        status = "RED"
    elif yellow > 0:
        status = "YELLOW"
    else:
        status = "GREEN"

    # =========================
    # SMARTCARGO-AIPA RECOMMENDATIONS
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
        recommendations=recommendations
    )

# =========================
# BUSINESS LOGIC
# =========================
def generate_recommendations(status: str, red: int, yellow: int) -> list[str]:
    recs = []

    if status == "GREEN":
        recs.append("Cargo accepted for processing.")
        recs.append("Proceed with build-up and flight planning.")
        recs.append("Maintain current compliance standards.")

    elif status == "YELLOW":
        recs.append("Cargo conditionally accepted.")
        recs.append("Review documentation and physical handling issues.")
        recs.append("Supervisor verification recommended before release.")
        recs.append("Re-check temperature, labeling, and segregation if applicable.")

    elif status == "RED":
        recs.append("Cargo NOT accepted.")
        recs.append("Immediate corrective action required.")
        recs.append("Isolate cargo and notify supervisor.")
        recs.append("Do not proceed until all critical issues are resolved.")
        recs.append("Document non-compliance per AIPA cargo standards.")

    # Risk weighting guidance
    if red >= 3:
        recs.append("Multiple critical failures detected – escalate to management.")
    if yellow >= 5:
        recs.append("High number of warnings – conduct full secondary inspection.")

    return recs

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "OK", "system": "SMARTCARGO-AIPA"}
