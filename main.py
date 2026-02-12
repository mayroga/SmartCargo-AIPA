from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import os

# =========================
# APP
# =========================
app = FastAPI(
    title="SMARTCARGO-AIPA",
    version="1.0"
)

# =========================
# FRONTEND (REAL)
# =========================
FRONTEND_DIR = "frontend"
INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# =========================
# MODELS
# =========================
class CargoValidation(BaseModel):
    answers: Dict[str, str]   # q1: ok|warn|fail
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
def root():
    if not os.path.exists(INDEX_FILE):
        return HTMLResponse(
            "<h2>frontend/index.html NOT FOUND</h2>",
            status_code=500
        )
    return FileResponse(INDEX_FILE)

@app.post("/validate", response_model=ValidationResult)
def validate_cargo(data: CargoValidation):

    TOTAL_QUESTIONS = 49
    green = yellow = red = 0

    for value in data.answers.values():
        if value == "ok":
            green += 1
        elif value == "warn":
            yellow += 1
        elif value == "fail":
            red += 1

    # =========================
    # SEMÁFORO
    # =========================
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
        total_questions=TOTAL_QUESTIONS,
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recommendations
    )

# =========================
# LOGIC
# =========================
def generate_recommendations(status: str, red: int, yellow: int) -> List[str]:
    recs = []

    if status == "GREEN":
        recs += [
            "Cargo accepted for processing.",
            "Proceed with build-up and flight planning.",
            "No operational restrictions detected."
        ]

    if status == "YELLOW":
        recs += [
            "Cargo conditionally accepted.",
            "Correct warnings before release.",
            "Supervisor approval required.",
            "Re-check labels, documentation, temperature, and segregation."
        ]

    if status == "RED":
        recs += [
            "Cargo NOT accepted.",
            "Immediate stop of operation.",
            "Isolate cargo and notify supervisor.",
            "Correct all critical failures before revalidation.",
            "Record non-compliance per AIPA / airline procedures."
        ]

    if red >= 3:
        recs.append("Multiple critical failures – escalate to management immediately.")

    if yellow >= 5:
        recs.append("High operational risk – perform full secondary inspection.")

    return recs

# =========================
# HEALTH
# =========================
@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "SMARTCARGO-AIPA"
    }

# =========================
# LOCAL RUN (OPTIONAL)
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
