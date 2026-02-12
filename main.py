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
# 49 PREGUNTAS REALES FUNCIONALES
# =========================
questions = [
    {"id":"q1","question":"AWB original legible y sin tachaduras","role":"Forwarder","type":"text"},
    {"id":"q2","question":"Altura del bulto dentro de límites Avianca (cm)","role":"Counter","type":"number","max_cm":80,"max_freighter":244},
    {"id":"q3","question":"Camión refrigerado si carga Pharma/Perecederos","role":"Trucker","type":"boolean"},
    {"id":"q4","question":"Temperatura registrada dentro de rango","role":"Trucker","type":"number","min_temp":2,"max_temp":8},
    {"id":"q5","question":"Embalaje DG aprobado según UN","role":"DG","type":"boolean"},
    {"id":"q6","question":"Etiquetas visibles y correctas (DG/Fragile/Perecedero)","role":"Counter","type":"boolean"},
    {"id":"q7","question":"Peso y volumen coinciden con documentación","role":"Counter","type":"number"},
    {"id":"q8","question":"Documentos Human Remains completos","role":"Forwarder","type":"boolean"},
    {"id":"q9","question":"Dry Ice declarado y etiquetado correctamente","role":"DG","type":"boolean"},
    {"id":"q10","question":"Pallet correctamente armado y estable","role":"Trucker","type":"boolean"},
    {"id":"q11","question":"Sello del camión presente y sin daños","role":"Trucker","type":"boolean"},
    {"id":"q12","question":"Carga asegurada y estable","role":"Trucker","type":"boolean"},
    {"id":"q13","question":"Shipper coincide con AWB y facturas","role":"Forwarder","type":"boolean"},
    {"id":"q14","question":"House / Master AWB alineados","role":"Forwarder","type":"boolean"},
    {"id":"q15","question":"Packing list completo y legible","role":"Forwarder","type":"boolean"},
    {"id":"q16","question":"Facturas coinciden con AWB","role":"Forwarder","type":"boolean"},
    {"id":"q17","question":"Permisos y certificados presentes","role":"Forwarder","type":"boolean"},
    {"id":"q18","question":"Tipo de carga correctamente declarado en papel","role":"Owner","type":"boolean"},
    {"id":"q19","question":"Peso declarado coincide con carga física","role":"Owner","type":"number"},
    {"id":"q20","question":"Fragile declarado y embalaje correcto","role":"Counter","type":"boolean"},
    {"id":"q21","question":"Tipo de pallet adecuado","role":"Trucker","type":"boolean"},
    {"id":"q22","question":"Pallet envuelto correctamente","role":"Trucker","type":"boolean"},
    {"id":"q23","question":"Etiquetas de temperatura visibles","role":"Counter","type":"boolean"},
    {"id":"q24","question":"No mezcla de mercancías incompatibles","role":"Counter","type":"boolean"},
    {"id":"q25","question":"Carga estable y segura en camión","role":"Counter","type":"boolean"},
    {"id":"q26","question":"Clasificación Pharma correcta","role":"Forwarder","type":"boolean"},
    {"id":"q27","question":"Rango de temperatura declarado en AWB","role":"Forwarder","type":"number","min_temp":2,"max_temp":8},
    {"id":"q28","question":"SLI firmado correctamente","role":"Forwarder","type":"boolean"},
    {"id":"q29","question":"Packaging validado según normas Avianca","role":"Counter","type":"boolean"},
    {"id":"q30","question":"MSDS presente si aplica","role":"DG","type":"boolean"},
    {"id":"q31","question":"Fechas de caducidad legibles","role":"Counter","type":"boolean"},
    {"id":"q32","question":"DG declarado en AWB","role":"DG","type":"boolean"},
    {"id":"q33","question":"Clase DG correcta","role":"DG","type":"text"},
    {"id":"q34","question":"DGD firmada","role":"DG","type":"boolean"},
    {"id":"q35","question":"Embalaje UN aprobado","role":"DG","type":"boolean"},
    {"id":"q36","question":"Labels DG visibles","role":"DG","type":"boolean"},
    {"id":"q37","question":"DG no mezclado con otra carga","role":"DG","type":"boolean"},
    {"id":"q38","question":"Ataúd conforme y embalaje seguro","role":"Counter","type":"boolean"},
    {"id":"q39","question":"Packing list separado y completo para Human Remains","role":"Forwarder","type":"boolean"},
    {"id":"q40","question":"Documentación Human Remains correcta (AWB, permisos)","role":"Counter","type":"boolean"},
    {"id":"q41","question":"Tiempo de tránsito compatible","role":"Forwarder","type":"boolean"},
    {"id":"q42","question":"Temperatura y ventilación correcta","role":"Counter","type":"boolean"},
    {"id":"q43","question":"Peso total validado","role":"Counter","type":"number"},
    {"id":"q44","question":"Facturas y packing list organizados","role":"Forwarder","type":"boolean"},
    {"id":"q45","question":"Docs consolidados correctos","role":"Forwarder","type":"boolean"},
    {"id":"q46","question":"Apto belly cargo","role":"Counter","type":"boolean"},
    {"id":"q47","question":"No mezcla con DG / Perecedero","role":"Counter","type":"boolean"},
    {"id":"q48","question":"Checklist completo revisado","role":"Counter","type":"boolean"},
    {"id":"q49","question":"Recomendaciones y responsables claros","role":"Counter","type":"boolean"},
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
        if q["type"] == "number" and ans is not None:
            try:
                val = float(ans)
                max_val = q.get("max_cm")
                min_val = q.get("min_temp")
                max_temp = q.get("max_temp")
                if max_val and val > max_val:
                    ans = "fail"
                elif min_val is not None and max_temp is not None and not (min_val <= val <= max_temp):
                    ans = "fail"
                else:
                    ans = "ok"
            except:
                ans = "fail"

        elif q["type"] == "boolean":
            if ans in [True,"true","ok"]:
                ans = "ok"
            elif ans in [False,"false","fail"]:
                ans = "fail"
            else:
                ans = "warn"

        elif q["type"] == "text":
            if ans and ans.strip() != "":
                ans = "ok"
            else:
                ans = "fail"

        # Contar colores semáforo
        if ans == "ok":
            green += 1
        elif ans == "warn":
            yellow += 1
        else:
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

    # Recomendaciones adicionales
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
