# main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
import io
from weasyprint import HTML

# =========================
# APP SETUP
# =========================
app = FastAPI(title="SMARTCARGO-AIPA", version="1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =========================
# LOGIN SIMPLE
# =========================
USERS_DB = {
    "admin": "1234",
    "supervisor": "cargo2026"
}

def authenticate_user(username: str, password: str):
    if username in USERS_DB and USERS_DB[username] == password:
        return True
    return False

# =========================
# DATA MODELS
# =========================
class CargoValidation(BaseModel):
    answers: dict  # {"q1":"ok","q2":"warn","q3":"fail",...}
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
    recommendations: list[str]

# =========================
# ENDPOINTS
# =========================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if authenticate_user(username, password):
        return {"success": True, "username": username}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/validate", response_model=ValidationResult)
async def validate_cargo(data: CargoValidation):
    total_questions = 49
    green = yellow = red = 0

    # =========================
    # CASCADA LETAL SIMPLIFICADA
    # =========================
    answers_filtered = {}
    for qid, value in data.answers.items():
        # Aplicar lógica de cascada letal
        # Ejemplo: si DG, ignorar bloques de perecederos
        if "q1" in data.answers:
            cargo_type = data.answers["q1"]
            if cargo_type == "DG" and qid in ["q_temp1", "q_temp2"]:
                continue  # Saltar preguntas irrelevantes
            if cargo_type == "Perishable" and qid in ["q_dg1", "q_dg2"]:
                continue
        answers_filtered[qid] = value

        if value == "ok":
            green += 1
        elif value == "warn":
            yellow += 1
        elif value == "fail":
            red += 1

    # =========================
    # SEMAFORO
    # =========================
    if red > 0:
        status = "RED"
    elif yellow > 0:
        status = "YELLOW"
    else:
        status = "GREEN"

    recommendations = generate_recommendations(status, red, yellow)

    # Guardar para PDF
    report_id = f"SCR-{uuid.uuid4().hex[:8].upper()}"
    return ValidationResult(
        report_id=report_id,
        timestamp=datetime.utcnow().isoformat(),
        operator=data.operator,
        total_questions=total_questions,
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recommendations
    )

@app.get("/pdf/{report_id}")
async def get_pdf(report_id: str, operator: str = "Unknown", status: str = "GREEN", recs: str = ""):
    """
    Genera PDF de Certificado de Conformidad con blindaje legal y autopropaganda.
    """
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>SmartCargo-AIPA Certificate</title>
        <style>
            body {{ font-family: "Segoe UI", Arial, sans-serif; background: #f9f9f9; }}
            .container {{ max-width: 800px; margin: 30px auto; background: white; padding: 30px; border-radius: 14px; }}
            h1 {{ color: #002b5c; }}
            h2 {{ color: #004080; }}
            .status-green {{ color: #0a8f08; }}
            .status-yellow {{ color: #d4a000; }}
            .status-red {{ color: #c00000; }}
            .recs {{ margin-top: 20px; font-size: 14px; }}
            footer {{ font-size: 11px; color: #555; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Certificado de Conformidad - SmartCargo-AIPA</h1>
            <h2>Report ID: {report_id}</h2>
            <p>Operador: {operator}</p>
            <p>Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <h2>Status:</h2>
            <p class="status-{status.lower()}">{status}</p>
            <div class="recs">
                <h3>Recomendaciones:</h3>
                <p>{recs.replace('|','<br>')}</p>
            </div>
            <footer>
                SmartCargo-AIPA by May Roga LLC<br>
                Este reporte constituye asesoría técnica preventiva basada en los datos proporcionados.<br>
                No sustituye la autoridad final de CBP, TSA o aerolínea.<br>
                Use bajo su responsabilidad.
            </footer>
        </div>
    </body>
    </html>
    """

    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    return FileResponse(pdf_file, media_type='application/pdf', filename=f"{report_id}.pdf")

# =========================
# LOGIC FOR RECOMMENDATIONS
# =========================
def generate_recommendations(status: str, red: int, yellow: int) -> list[str]:
    recs = []

    if status == "GREEN":
        recs.append("Cargo aceptado para procesamiento|Proceda con armado y planificación de vuelo|Mantener estándares de cumplimiento actuales")
    elif status == "YELLOW":
        recs.append("Cargo aceptado condicionalmente|Revise documentación y manejo físico|Verificación del supervisor antes de liberación|Re-chequear temperatura, etiquetado y segregación si aplica")
    elif status == "RED":
        recs.append("Cargo NO aceptado|Acción correctiva inmediata requerida|Aislar carga y notificar supervisor|No proceder hasta que todos los problemas críticos estén resueltos|Documentar incumplimiento según estándares AIPA")

    if red >= 3:
        recs.append("Múltiples fallos críticos detectados – escalar a gerencia")
    if yellow >= 5:
        recs.append("Número elevado de advertencias – realizar inspección secundaria completa")

    return recs

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "OK", "system": "SMARTCARGO-AIPA"}
