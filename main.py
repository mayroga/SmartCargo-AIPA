from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="SMARTCARGO-AIPA", version="1.0")

# Permitir CORS para conexión con frontend local
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
    answers: dict  # Recibe {"q1": "ok", "q2": "fail", ...}
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
# 49 PREGUNTAS CONFIGURADAS
# =========================
questions = [
    {"id":"q1","question":"AWB original legible","role":"Owner"},
    {"id":"q2","question":"Factura y packing list completos","role":"Owner"},
    {"id":"q3","question":"Declaración coincide con documentos","role":"Owner"},
    {"id":"q4","question":"Permisos y certificados presentes","role":"Owner"},
    {"id":"q5","question":"Peso declarado coincide con carga","role":"Owner"},
    {"id":"q6","question":"Tipo de carga declarada en papel","role":"Owner"},
    {"id":"q7","question":"Shipper coincide con AWB","role":"Owner"},
    {"id":"q8","question":"Docs Human Remains completos","role":"Owner"},
    {"id":"q9","question":"Camión refrigerado adecuado","role":"Trucker"},
    {"id":"q10","question":"Camión limpio y seguro","role":"Trucker"},
    {"id":"q11","question":"Sello del camión presente","role":"Trucker"},
    {"id":"q12","question":"Carga asegurada y estable","role":"Trucker"},
    {"id":"q13","question":"Temperatura registrada correctamente","role":"Trucker"},
    {"id":"q14","question":"Pallet y embalaje adecuado","role":"Trucker"},
    {"id":"q15","question":"AWB coincidente con documentos","role":"Forwarder"},
    {"id":"q16","question":"House / Master AWB alineados","role":"Forwarder"},
    {"id":"q17","question":"Packaging revisado y aprobado","role":"Forwarder"},
    {"id":"q18","question":"Temperatura declarada compatible","role":"Forwarder"},
    {"id":"q19","question":"Dry Ice declarado y etiquetado","role":"Forwarder"},
    {"id":"q20","question":"Fragile declarado y embalaje","role":"Forwarder"},
    {"id":"q21","question":"Docs Human Remains completos","role":"Forwarder"},
    {"id":"q22","question":"Altura dentro de límite Avianca","role":"Counter"},
    {"id":"q23","question":"Largo y ancho dentro de límite","role":"Counter"},
    {"id":"q24","question":"Peso por pie cuadrado seguro","role":"Counter"},
    {"id":"q25","question":"Carga estable y segura","role":"Counter"},
    {"id":"q26","question":"No mezcla DG/Pharma/Perecedero","role":"Counter"},
    {"id":"q27","question":"Etiquetas visibles y legibles","role":"Counter"},
    {"id":"q28","question":"Verificación docs completa","role":"Counter"},
    {"id":"q29","question":"DG declarado en AWB","role":"DG"},
    {"id":"q30","question":"Clase DG correcta","role":"DG"},
    {"id":"q31","question":"DGD y MSDS firmados","role":"DG"},
    {"id":"q32","question":"Embalaje UN aprobado","role":"DG"},
    {"id":"q33","question":"Labels DG visibles","role":"DG"},
    {"id":"q34","question":"DG no mezclado","role":"DG"},
    {"id":"q35","question":"Ataúd conforme y embalaje","role":"Human Remains"},
    {"id":"q36","question":"Packing list separado","role":"Human Remains"},
    {"id":"q37","question":"Docs Human Remains correctos","role":"Human Remains"},
    {"id":"q38","question":"Tiempo tránsito compatible","role":"Human Remains"},
    {"id":"q39","question":"Temperatura y ventilación","role":"Human Remains"},
    {"id":"q40","question":"Peso total validado","role":"Human Remains"},
    {"id":"q41","question":"Facturas y packing organizados","role":"Human Remains"},
    {"id":"q42","question":"Peso coincidente documentos","role":"Human Remains"},
    {"id":"q43","question":"Docs consolidados correctos","role":"Human Remains"},
    {"id":"q44","question":"Apto belly cargo","role":"Human Remains"},
    {"id":"q45","question":"No mezcla DG / Perecedero","role":"Human Remains"},
    {"id":"q46","question":"Checklist completo revisado","role":"Human Remains"},
    {"id":"q47","question":"Peso bulto y pallets verificado","role":"Human Remains"},
    {"id":"q48","question":"Revisión final semáforo","role":"Human Remains"},
    {"id":"q49","question":"Recomendaciones claras","role":"Human Remains"},
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

    # Procesar cada respuesta enviada por el HTML
    for q in questions:
        ans = data.answers.get(q["id"])
        
        # Como el HTML envía directamente "ok", "warn", o "fail"
        if ans == "ok":
            green += 1
        elif ans == "warn":
            yellow += 1
        elif ans == "fail" or ans is None:
            red += 1

    # Lógica de Asesoría para el estatus
    if red > 0:
        status = "RED"
        recs.append("Carga NO apta para despacho. Corregir puntos en rojo.")
    elif yellow > 0:
        status = "YELLOW"
        recs.append("Carga aceptada con observaciones. Notificar a la estación.")
    else:
        status = "GREEN"
        recs.append("Carga verificada. Proceder con el manifiesto.")

    # Alertas de peso específico
    if red >= 3:
        recs.append("Alerta: Múltiples discrepancias críticas detectadas.")
    if yellow >= 5:
        recs.append("Aviso: Requiere supervisión por acumulación de advertencias.")

    return ValidationResult(
        report_id=f"SCR-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow().isoformat(),
        operator=data.operator if data.operator else "Unknown",
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
