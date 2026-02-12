from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional, Dict, List

# =========================
# APP INSTANCE
# =========================
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
    answers: Dict[str, str]  # {"q1":"ok","q2":"warn","q3":"fail",...}
    operator: Optional[str] = "Unknown"

class ValidationResult(BaseModel):
    report_id: str
    timestamp: str
    operator: str
    total_questions: int
    green: int
    yellow: int
    red: int
    status: str
    recommendations: List[str]

# =========================
# ROUTES
# =========================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/validate", response_model=ValidationResult)
async def validate_cargo(data: CargoValidation):
    """Validate cargo answers and return status with recommendations"""
    total_questions = 49
    green = yellow = red = 0

    # Count green, yellow, red based on answers
    for value in data.answers.values():
        if value == "ok":
            green += 1
        elif value == "warn":
            yellow += 1
        elif value == "fail":
            red += 1

    # Determine overall status
    if red > 0:
        status = "RED"
    elif yellow > 0:
        status = "YELLOW"
    else:
        status = "GREEN"

    recommendations = generate_recommendations(status, red, yellow)

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
def generate_recommendations(status: str, red: int, yellow: int) -> List[str]:
    recs: List[str] = []

    if status == "GREEN":
        recs.extend([
            "Cargo accepted for processing.",
            "Proceed with build-up and flight planning.",
            "Maintain current compliance standards."
        ])
    elif status == "YELLOW":
        recs.extend([
            "Cargo conditionally accepted.",
            "Review documentation and physical handling issues.",
            "Supervisor verification recommended before release.",
            "Re-check temperature, labeling, and segregation if applicable."
        ])
    elif status == "RED":
        recs.extend([
            "Cargo NOT accepted.",
            "Immediate corrective action required.",
            "Isolate cargo and notify supervisor.",
            "Do not proceed until all critical issues are resolved.",
            "Document non-compliance per AIPA cargo standards."
        ])

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
    """Health check endpoint"""
    return {"status": "OK", "system": "SMARTCARGO-AIPA"}

# =========================
# RUN LOCAL SERVER (optional)
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
