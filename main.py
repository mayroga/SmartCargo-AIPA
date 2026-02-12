from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

# Importación de la autoridad desde models.py
from models import (
    CargoAnswer, 
    ValidationResult, 
    AlertLevel, 
    QUESTIONS_DB, 
    generate_report_id, 
    get_legal_disclaimer
)

app = FastAPI(title="SMARTCARGO BY MAY ROGA LLC", version="2.0")

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
# RUTA RAÍZ (INTERFAZ VISUAL)
# =========================
@app.get("/", response_class=HTMLResponse)
def get_interface():
    """
    Esta función permite que al entrar a la URL veas la App, no solo texto.
    Carga el contenido del index.html directamente.
    """
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body style='font-family:sans-serif; text-align:center; padding-top:50px;'>
                <h1 style='color:#d8232a;'>SMARTCARGO BY MAY ROGA LLC</h1>
                <p>Error: Archivo index.html no encontrado en el servidor.</p>
            </body>
        </html>
        """

# =========================
# RUTAS DE DATOS (API)
# =========================

@app.get("/questions")
def get_questions():
    """Retorna la base de conocimiento técnica de models.py"""
    return QUESTIONS_DB

@app.post("/validate", response_model=ValidationResult)
def validate_cargo(data: CargoAnswer):
    """Motor de Asesoría: Procesa respuestas y emite dictamen legal"""
    green = yellow = red = 0
    recommendations = []

    for q_item in QUESTIONS_DB:
        q_id = q_item["id"]
        ans_value = data.answers.get(q_id, "fail")
        desc = q_item["description"]
        
        if ans_value == "ok":
            green += 1
        elif ans_value == "warn":
            yellow += 1
            recommendations.append(f"ADVERTENCIA en {q_id}: {desc}")
        else:
            red += 1
            recommendations.append(f"RECHAZO CRÍTICO en {q_id}: {desc}")

    # Semáforo de autoridad
    if red > 0:
        status = AlertLevel.RED
        recommendations.insert(0, "DICTAMEN: CARGA NO APTA. Incumplimiento de seguridad.")
    elif yellow > 0:
        status = AlertLevel.YELLOW
        recommendations.insert(0, "DICTAMEN: ACEPTACIÓN CONDICIONADA. Verificar observaciones.")
    else:
        status = AlertLevel.GREEN
        recommendations.insert(0, "DICTAMEN: CUMPLIMIENTO TOTAL. Proceder con el embarque.")

    return ValidationResult(
        report_id=generate_report_id(),
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        operator=data.operator if data.operator else "Counter_Default",
        cargo_type=data.cargo_type.value,
        total_questions=len(QUESTIONS_DB),
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recommendations,
        legal_note=get_legal_disclaimer()
    )

@app.get("/health")
def health():
    return {"status": "ACTIVE", "provider": "SMARTCARGO BY MAY ROGA LLC"}
