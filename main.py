from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="SMARTCARGO BY MAY ROGA LLC", version="2.0")

# Configuración de CORS para asegurar conexión con el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# MODELOS DE DATOS (Pydantic)
# =========================
class CargoAnswer(BaseModel):
    answers: dict  # Recibe {"q1": "ok", "q2": "fail", ...}
    operator: str | None = "Unknown"
    cargo_type: str | None = "General"

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
    legal_note: str

# =========================
# BASE DE CONOCIMIENTO TÉCNICO (IATA/CBP/TSA/DOT)
# =========================
# Aquí se define la autoridad del sistema.
questions_db = [
    # --- BLOQUE DOCUMENTAL (CBP / IATA) ---
    {"id":"q1","q":"MAWB original legible + 3 copias (fuera del sobre)","tip":"Requerido para agilizar proceso de aceptación y archivo de estación."},
    {"id":"q2","q":"HMAWB y Manifiesto coinciden 100% con MAWB (Consolidados)","tip":"Discrepancias generan multas de aduana y retención de carga (CBP)."},
    {"id":"q3","q":"Factura Comercial y Packing List (Original + Copias)","tip":"Indispensable para valoración aduanera y desglose de bultos."},
    {"id":"q4","q":"EIN / Tax ID de Shipper y Consignatario en sistema","tip":"Dato obligatorio para transmisión AMS (Automated Manifest System)."},
    
    # --- BLOQUE SEGURIDAD (TSA) ---
    {"id":"q5","q":"Declaración de contenido coincide con Inspección Física/X-Ray","tip":"Requisito TSA. Contenido no declarado es motivo de rechazo inmediato."},
    {"id":"q6","q":"Sello de seguridad de camión presente y sin alteración","tip":"Garantiza la integridad de la cadena de custodia desde el origen."},
    
    # --- BLOQUE DIMENSIONES Y PESO (AVIANCA ENGINEERING) ---
    {"id":"q7","q":"Altura ≤ 80cm (Avión PAX) o ≤ 160cm (Carguero/Belly)","tip":"Límite físico de compuerta. Si excede, la carga no vuela en la ruta asignada."},
    {"id":"q8","q":"Peso por pie cuadrado ≤ 732 kg/m² (Shoring si aplica)","tip":"Evita daños estructurales en el suelo de la bodega de la aeronave."},
    {"id":"q9","q":"Carga sobre pallet, envuelta en stretch y con red de seguridad","tip":"Asegura estabilidad para evitar desplazamientos en vuelo."},
    
    # --- BLOQUE MERCANCÍAS PELIGROSAS (IATA DGR / DOT) ---
    {"id":"q10","q":"DGD firmada en original y Embalaje con Marcado UN","tip":"Mercancía peligrosa sin marcado normativo genera multas federales graves."},
    {"id":"q11","q":"Etiquetas de Riesgo y Manipulación visibles y legibles","tip":"Indispensable para la segregación correcta en bodega (No mezclar incompatibles)."},
    {"id":"q12","q":"MSDS (Hoja de Seguridad) adjunta al set documental","tip":"Requerida para protocolos de emergencia en caso de derrame."},
    
    # --- BLOQUE CADENA DE FRÍO (PHARMA / PERISHABLE) ---
    {"id":"q13","q":"Termógrafo activo y Rango térmico entre 2°C y 8°C","tip":"Garantiza la viabilidad del producto. Fuera de rango genera reclamos (Claims)."},
    {"id":"q14","q":"Embalaje térmico intacto (Gel packs / Hielo seco declarado)","tip":"El hielo seco debe estar declarado como DG por riesgo de asfixia."},
    
    # --- BLOQUE ESPECIALES (HUMAN REMAINS) ---
    {"id":"q15","q":"Permiso de Sanidad y Acta de Defunción Original","tip":"Documentación legal obligatoria para el transporte de restos humanos."},
    {"id":"q16","q":"Ataúd con embalaje hermético y caja exterior de madera/cartón","tip":"Cumplimiento de bioseguridad para evitar fugas de fluidos."},

    # ... Se pueden expandir hasta las 49 o más según necesidad de la estación ...
]

# =========================
# MOTOR DE ASESORÍA (LOGIC)
# =========================

@app.get("/questions")
def get_questions():
    return questions_db

@app.post("/validate", response_model=ValidationResult)
def validate_cargo(data: CargoAnswer):
    total = len(questions_db)
    green = yellow = red = 0
    recs = []

    # Análisis de cada respuesta enviada
    for q in questions_db:
        ans = data.answers.get(q["id"])
        
        if ans == "ok":
            green += 1
        elif ans == "warn":
            yellow += 1
            recs.append(f"OBSERVACIÓN en {q['id']}: {q['q']}. Verificar antes de paletizar.")
        else:
            red += 1
            recs.append(f"RECHAZO CRÍTICO en {q['id']}: {q['q']}. Acción: Detener recepción.")

    # Dictamen de Seguridad y Vuelo
    if red > 0:
        status = "RED - CARGA NO APTA"
        recs.insert(0, "DICTAMEN: Rechazo automático por incumplimiento de seguridad/normativa.")
    elif yellow > 0:
        status = "YELLOW - ACEPTACIÓN CONDICIONADA"
        recs.insert(0, "DICTAMEN: Carga requiere acción correctiva inmediata en counter.")
    else:
        status = "GREEN - LISTA PARA VUELO"
        recs.insert(0, "DICTAMEN: Cumplimiento total. Proceder con el pesado y etiquetado.")

    # Notas de Autoridad
    legal_info = "Reporte generado bajo normativas IATA, CBP, TSA y SOP de Avianca Cargo. SMARTCARGO BY MAY ROGA LLC."

    return ValidationResult(
        report_id=f"SCR-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        operator=data.operator if data.operator else "Counter_Default",
        total_questions=total,
        green=green,
        yellow=yellow,
        red=red,
        status=status,
        recommendations=recs,
        legal_note=legal_info
    )

@app.get("/health")
def health():
    return {"status":"ACTIVE","provider":"SMARTCARGO BY MAY ROGA LLC"}

# =========================
# NOTA DE EJECUCIÓN
# =========================
# Ejecutar con: uvicorn main:app --reload
