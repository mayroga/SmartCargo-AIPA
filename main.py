from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

from models import (
    CargoAnswer,
    ValidationResult,
    AlertLevel,
    QUESTIONS_DB,
    SmartCargoAdvisory,
    generate_report_id,
    get_legal_disclaimer
)

app = FastAPI(title="SMARTCARGO BY MAY ROGA LLC", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# INTERFAZ INTEGRADA
# =========================
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>SMARTCARGO BY MAY ROGA LLC</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        :root { --primary:#d8232a; --secondary:#003366; --accent:#f4f4f4; }
        body { font-family:'Segoe UI',sans-serif; margin:0; background:var(--accent); }
        header { background:var(--secondary); color:white; padding:20px; text-align:center; border-bottom:5px solid var(--primary);}
        .container { max-width:900px; margin:20px auto; background:white; padding:30px; border-radius:12px; box-shadow:0 5px 20px rgba(0,0,0,0.1);}
        .question-card { border-bottom:1px solid #eee; padding:15px 0; display:flex; justify-content:space-between; align-items:center;}
        .question-info { flex:2; }
        .question-desc { font-weight:bold; display:block; margin-bottom:5px; color:#333; }
        .question-tip { font-size:12px; color:#666; font-style:italic;}
        select { padding:10px; border-radius:5px; border:1px solid #ccc; font-weight:bold; cursor:pointer;}
        .actions { display:flex; gap:15px; margin-top:30px; }
        .btn { flex:1; padding:15px; border:none; border-radius:8px; cursor:pointer; font-weight:bold; text-transform:uppercase; color:white; transition:0.3s; }
        .btn-validate { background:var(--primary);}
        .btn-clear { background:#555;}
        .btn:hover { opacity:0.9; transform:translateY(-2px);}
        #result { margin-top:30px; padding:20px; border-radius:10px; display:none; border:2px solid #ccc;}
        .legal-note { font-size:11px; color:#777; margin-top:20px; text-align:center; border-top:1px solid #ddd; padding-top:10px;}
    </style>
</head>
<body>
<header>
    <h1>SMARTCARGO BY MAY ROGA LLC</h1>
    <p>Asesoría Técnica Especializada (IATA / CBP / TSA / DOT)</p>
</header>

<div class="container">
    <div id="questions-container"><p style="text-align:center;">Cargando estándares técnicos...</p></div>
    <div id="result"></div>
    <div class="actions">
        <button class="btn btn-validate" onclick="processValidation()">Validar Cumplimiento</button>
        <button class="btn btn-clear" onclick="location.reload()">Borrar Todo</button>
    </div>
    <div class="legal-note">© 2026 SMARTCARGO BY MAY ROGA LLC. Todos los derechos reservados.</div>
</div>

<script>
const API_BASE = window.location.origin;

async function loadQuestions() {
    try {
        const res = await axios.get(`${API_BASE}/questions`);
        const container = document.getElementById('questions-container');
        container.innerHTML = "";
        res.data.forEach(q => {
            container.innerHTML += `
                <div class="question-card">
                    <div class="question-info">
                        <span class="question-desc">${q.description}</span>
                        <span class="question-tip">${q.tip} (${q.authority})</span>
                    </div>
                    <select id="${q.id}">
                        <option value="ok">CUMPLE</option>
                        <option value="warn">OBSERVACIÓN</option>
                        <option value="fail">RECHAZO</option>
                    </select>
                </div>`;
        });
    } catch (e) {
        alert("Error de conexión con el sistema central.");
    }
}

async function processValidation() {
    const selects = document.querySelectorAll('select');
    const answers = {};
    selects.forEach(s => { answers[s.id] = s.value; });

    const operator = prompt("IDENTIFICACIÓN DEL OPERADOR:", "COUNTER_AV");

    try {
        const res = await axios.post(`${API_BASE}/validate`, {
            answers: answers,
            operator: operator,
            cargo_type: "General Cargo"
        });
        const d = res.data;
        const resDiv = document.getElementById('result');
        resDiv.style.display = "block";
        resDiv.style.background = d.red > 0 ? "#f8d7da" : d.yellow > 0 ? "#fff3cd" : "#d4edda";
        resDiv.innerHTML = `
            <h2 style="margin:0; color:#333;">${d.status}</h2>
            <p><strong>REPORT ID:</strong> ${d.report_id} | <strong>OPERADOR:</strong> ${d.operator}</p>
            <hr>
            <strong>RECOMENDACIONES:</strong>
            <ul style="font-size:14px;">${d.recommendations.map(r => `<li>${r}</li>`).join("")}</ul>
            <hr>
            <h4>Ganancia Protegida</h4>
            <p>Peso Declarado: ${d.chargeable_weight} kg</p>
            <p>Peso Verificado SmartCargo: ${d.verified_weight} kg</p>
            <p>Ajuste Sugerido: ${d.weight_adjustment} kg</p>
            <p style="font-size:11px; font-style:italic;">${d.legal_note}</p>
        `;
        resDiv.scrollIntoView({behavior: "smooth"});
    } catch (e) { alert("Error al procesar validación técnica."); }
}

loadQuestions();
</script>
</body>
</html>
"""

# =========================
# RUTAS
# =========================

@app.get("/", response_class=HTMLResponse)
def get_interface():
    return HTML_CONTENT

@app.get("/questions")
def get_questions():
    return QUESTIONS_DB

@app.post("/validate", response_model=ValidationResult)
def validate_cargo(data: CargoAnswer):
    advisor = SmartCargoAdvisory(data)
    report = advisor.get_report()
    return report
