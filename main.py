from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

# Importación de la lógica y modelos desde models.py
# Asegúrate de que models.py esté en la misma carpeta
from models import (
    CargoAnswer, 
    ValidationResult, 
    AlertLevel, 
    QUESTIONS_DB, 
    generate_report_id, 
    get_legal_disclaimer
)

app = FastAPI(
    title="SMARTCARGO BY MAY ROGA LLC", 
    version="2.0",
    description="Sistema de cumplimiento técnico IATA, CBP, TSA y DOT"
)

# =========================
# CONFIGURACIÓN DE SEGURIDAD (CORS)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# RUTAS DE LA API
# =========================

@app.get("/")
def home():
    """Ruta raíz para verificar que el servicio está LIVE en Render"""
    return {
        "service": "SMARTCARGO BY MAY ROGA LLC",
        "status": "OPERATIONAL",
        "authority": "IATA/CBP/TSA/DOT compliant"
    }

@app.get("/questions")
def get_questions():
    """Retorna la base de conocimiento técnica de models.py"""
    return QUESTIONS_DB

@app.post("/validate", response_model=ValidationResult)
def validate_cargo(data: CargoAnswer):
    """
    Motor de Asesoría: Procesa respuestas y emite un dictamen legal.
    No permite ambigüedades; si hay un fallo crítico (RED), la carga se detiene.
    """
    green = 0
    yellow = 0
    red = 0
    recommendations = []

    # Buscamos cada pregunta de la DB técnica para validar la respuesta del frontend
    for q_item in QUESTIONS_DB:
        q_id = q_item["id"]
        # Obtenemos la respuesta del usuario para ese ID (por defecto 'fail' si no llega)
        ans_value = data.answers.get(q_id, "fail")
        
        if ans_value == "ok":
            green += 1
        elif ans_value == "warn":
            yellow += 1
            recommendations.append(
                f"OBSERVACIÓN TÉCNICA ({q_id}): {q_item['description']}. Requiere verificación manual."
            )
        else:
            red += 1
            recommendations.append(
                f"RECHAZO CRÍTICO ({q_id}): {q_item['description']}. Acción: Detener recepción de carga."
            )

    # Determinar el semáforo final de autoridad
    if red > 0:
        final_status = AlertLevel.RED
        recommendations.insert(0, "DICTAMEN FINAL: CARGA NO APTA PARA VUELO. Incumplimiento de normativa de seguridad.")
    elif yellow > 0:
        final_status = AlertLevel.YELLOW
        recommendations.insert(0, "DICTAMEN FINAL: ACEPTACIÓN CONDICIONADA. Corregir observaciones antes del pesaje.")
    else:
        final_status = AlertLevel.GREEN
        recommendations.insert(0, "DICTAMEN FINAL: CUMPLIMIENTO TOTAL. Proceder con el embarque y etiquetado.")

    # Construcción del reporte basado en la estructura de models.py
    return ValidationResult(
        report_id=generate_report_id(),
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        operator=data.operator if data.operator else "Counter_Default",
        cargo_type=data.cargo_type.value,
        total_questions=len(QUESTIONS_DB),
        green=green,
        yellow=yellow,
        red=red,
        status=final_status,
        recommendations=recommendations,
        legal_note=get_legal_disclaimer()
    )

@app.get("/health")
def health():
    """Endpoint para monitoreo de Render"""
    return {"status": "ACTIVE", "provider": "SMARTCARGO BY MAY ROGA LLC"}

# =========================
# NOTA DE EJECUCIÓN
# =========================
# Para desarrollo local: uvicorn main:app --reload
# Para Render (Automático): uvicorn main:app --host 0.0.0.0 --port $PORT
