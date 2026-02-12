from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="SMARTCARGO-AIPA", version="1.0")

# Permitir CORS desde cualquier frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# MODELOS
# =========================
class CargoAnswer(BaseModel):
    answers: dict  # {"q1": "ok"/"warn"/"fail"}
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
# PREGUNTAS REALES
# =========================
questions = [
    {"id":"q1","question":"AWB original legible y sin tachaduras","role":"Forwarder","type":"text"},
    {"id":"q2","question":"Altura del bulto dentro de límites Avianca","role":"Counter","type":"number","max_cm":80,"max_freighter":244},
    {"id":"q3","question":"Camión refrigerado si carga Pharma/Perecederos","role":"Trucker","type":"boolean"},
    {"id":"q4","question":"Temperatura registrada dentro de rango","role":"Trucker","type":"number"},
    {"id":"q5","question":"Embalaje DG aprobado según UN","role":"DG","type":"boolean"},
    {"id":"q6","question":"Etiquetas visibles y correctas (DG/Fragile/Perecedero)","role":"Counter","type":"boolean"},
    {"id":"q7","question":"Peso y volumen coinciden con documentación","role":"Counter","type":"number"},
    {"id":"q8","question":"Documentos Human Remains completos","role":"Forwarder","type":"boolean"},
    {"id":"q9","question":"Dry Ice declarado y etiquetado correctamente","role":"DG","type":"boolean"},
    {"id":"q10","question":"Pallet correctamente armado y estable","role":"Trucker","type":"boolean"},
    # ... continuar hasta 49 preguntas reales siguiendo el mismo patrón
]

# =========================
# ENDPOINTS
# =========================
@app.get("/questions")
def get_questions():
    return questions

@app.post("/validate", response_model=ValidationResult)
def validate_cargo(data: CargoAnswer):
    total = len(questions)
    green = yellow = red = 0
    recs = []

    for q in questions:
        ans = data.answers.get(q["id"])
        # Validación según tipo de pregunta
        if q.get("type") == "number" and ans is not None:
            try:
                val = float(ans)
                max_val = q.get("max_cm", None)
                if max_val and val > max_val:
                    ans = "fail"
                else:
                    ans = "ok"
            except:
                ans = "fail"

        if ans == "ok":
            green += 1
        elif ans == "warn":
            yellow += 1
        elif ans == "fail" or ans is None:
            red += 1

    # Determinar semáforo
    if red > 0:
        status = "RED"
        recs.append("Cargo NO aceptado. Revisar inmediatamente los puntos críticos.")
    elif yellow > 0:
        status = "YELLOW"
        recs.append("Cargo con observaciones. Revisar antes de embarque.")
    else:
        status = "GREEN"
        recs.append("Cargo listo para embarque.")

    # Recomendaciones adicionales según fallos
    if red >= 3:
        recs.append("Múltiples fallos críticos, contactar supervisor o DG.")
    if yellow >= 5:
        recs.append("Alto número de advertencias, re-inspección recomendada.")

    return ValidationResult(
        report_id=f"SCR-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow().isoformat(),
        operator=data.operator,
        total_questions=total,
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recs
    )

@app.get("/health")
def health():
    return {"status":"OK","system":"SMARTCARGO-AIPA"}
