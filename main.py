from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from google import genai
from google.genai import types

# =====================================================
# CONFIGURACIÓN BÁSICA
# =====================================================
app = FastAPI(title="SmartCargo-AIPA Backend")

# Permitir que el frontend acceda
origins = [
    "https://smartcargo-advisory.onrender.com", 
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# VARIABLES DE ENTORNO
# =====================================================
# Asegúrate de configurar esta variable en el entorno de Render o localmente
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# =====================================================
# MOCK DATABASE Y REGLAS DE NEGOCIO
# =====================================================
cargas_db = []
documents_db = []
alertas_db = []
alertas_count = 0

rules_db = [
    {"rule_id": "R001", "source": "IATA", "category": "DG", "severity": "CRITICAL", "message_es": "Falta etiqueta de Manejo DG (IATA 5.2.1) o placard de transporte terrestre.", "message_en": "Missing DG Handling Label (IATA 5.2.1) or ground transport placard."},
    {"rule_id": "R002", "source": "ISPM15", "category": "Pallet", "severity": "CRITICAL", "message_es": "Pallet de madera sin certificación ISPM-15. Riesgo de retención fitosanitaria.", "message_en": "Wooden pallet without ISPM-15 certification. Phytosanitary retention risk."},
    {"rule_id": "R003", "source": "Aerolínea", "category": "Embalaje", "severity": "WARNING", "message_es": "Altura excede el máximo permitido (180cm). Riesgo de rechazo en rampa.", "message_en": "Height exceeds maximum allowed (180cm). Risk of rejection at ramp."},
    {"rule_id": "R004", "source": "Compatibilidad", "category": "Mercancía", "severity": "CRITICAL", "message_es": "Mercancía DG incompatible (por segregación IATA/IMDG) con otros artículos consolidados.", "message_en": "DG goods incompatible (due to IATA/IMDG segregation) with other consolidated items."},
    {"rule_id": "R005", "source": "Documentos", "category": "AWB", "severity": "WARNING", "message_es": "AWB, Packing List y Peso NO concuerdan (Inconsistencia documental).", "message_en": "AWB, Packing List and Weight DO NOT match (Documentary inconsistency)."},
]

# =====================================================
# FUNCIONES DE LÓGICA DE AIPA
# =====================================================
def validate_cargo(carga_data):
    """Ejecuta el Motor de Reglas de AIPA (Simulación)."""
    global alertas_count
    generated_alerts = []
    
    tipo_carga = carga_data.get("tipo_carga", "").lower()
    
    # Simulación de Incompatibilidad (R004)
    if tipo_carga == "quimicos" or tipo_carga == "dg":
        if carga_data.get("inconsistencias", 0) > 4: 
            rule = next((r for r in rules_db if r["rule_id"] == "R004"], None)
            if rule:
                alertas_count += 1
                generated_alerts.append({"id": str(uuid.uuid4()), "carga_id": carga_data["id"], "mensaje": rule["message_es"], "nivel": rule["severity"], "fecha": str(datetime.utcnow())})
                
    # Simulación de Pallet (R002)
    if carga_data.get("pallet_type", "madera") == "madera" and not carga_data.get("ispm15_verified", False):
        rule = next((r for r in rules_db if r["rule_id"] == "R002"], None)
        if rule:
            alertas_count += 1
            generated_alerts.append({"id": str(uuid.uuid4()), "carga_id": carga_data["id"], "mensaje": rule["message_es"], "nivel": rule["severity"], "fecha": str(datetime.utcnow())})

    # Simulación de Altura (R003)
    if carga_data.get("height_cm", 0) > 180:
        rule = next((r for r in rules_db if r["rule_id"] == "R003"], None)
        if rule:
            alertas_count += 1
            generated_alerts.append({"id": str(uuid.uuid4()), "carga_id": carga_data["id"], "mensaje": rule["message_es"], "nivel": rule["severity"], "fecha": str(datetime.utcnow())})

    alertas_db.extend(generated_alerts)
    carga_data["alertas"] = len(generated_alerts)
    carga_data["estado"] = "Revisión con Alertas" if generated_alerts else "Aprobada AIPA"
    
    return carga_data

# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/")
async def root():
    return {"message": "SmartCargo-AIPA Backend activo"}

# ------------------ CARGAS ------------------
@app.get("/cargas")
async def get_cargas():
    return {"cargas": cargas_db}

@app.post("/cargas")
async def create_carga(payload: dict):
    carga_id = str(uuid.uuid4())
    payload["id"] = carga_id
    payload["estado"] = "En revisión"
    payload["alertas"] = 0
    payload["fecha_creacion"] = str(datetime.utcnow())
    
    payload["inconsistencias"] = 0 
    payload["pallet_type"] = payload.get("pallet_type", "madera")
    payload["ispm15_verified"] = payload.get("ispm15_verified", False)
    payload["height_cm"] = payload.get("height_cm", 150)
    
    validated_carga = validate_cargo(payload)
    
    cargas_db.append(validated_carga)
    return {"id": carga_id, "alertas": validated_carga["alertas"]}

# ------------------ DOCUMENTOS ------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), carga_id: str = Form("N/A")):
    filename = f"{uuid.uuid4()}_{file.filename}"

    if "invoice" in filename.lower() and carga_id == "SC-AIPA-TEST-01":
        alerta = next((r for r in rules_db if r["rule_id"] == "R005"], None)
        if alerta:
            global alertas_count
            alertas_count += 1
            alertas_db.append({"id": str(uuid.uuid4()), "carga_id": carga_id, "mensaje": alerta["message_es"], "nivel": alerta["severity"], "fecha": str(datetime.utcnow())})
    
    documents_db.append({"id": str(uuid.uuid4()), "filename": filename, "carga_id": carga_id, "fecha_subida": str(datetime.utcnow())})
    
    return {"data": {"filename": filename, "carga_id": carga_id}}

# ------------------ ALERTAS ------------------
@app.get("/alertas")
async def get_alertas():
    sorted_alertas = sorted(alertas_db, key=lambda a: a['nivel'], reverse=True)
    return {"alertas": sorted_alertas}

# ------------------ ADVISORY (SMARTCARGO CONSULTING) ------------------
@app.post("/advisory")
async def advisory(question: str = Form(...)):
    if not GEMINI_API_KEY:
        return JSONResponse({"error":"GEMINI_API_KEY no configurada. Asesoría IA (SmartCargo Consulting) inactiva."}, status_code=500)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # 💡 INSTRUCCIÓN DE SISTEMA FINAL: ROL DE ASESORÍA NO-OPERATIVA REFORZADO
        system_instruction = (
            "Eres SMARTCARGO CONSULTING, el ASESOR PREVENTIVO VIRTUAL. **NO ERES** Inspector, TSA, Handler, Forwarder, Aerolínea, ni Operador Marítimo. "
            "Tu misión es proporcionar **asesoría experta** y anticiparte a los problemas que estas entidades podrían detectar, asegurando la garantía de destino de la carga. "
            "Tu valor es dar la misma perspectiva de un experto operativo/regulatorio, pero **sin ejecutar tareas físicas**: NO tocas, NO trasladas, NO cobras la carga, y NO realizas ninguna acción ilegal. Aunque no tienes licencias DG/HAZMAT operativas, tu asesoría sobre su cumplimiento regulatorio es fundamental. "
            "Tu expertise es el CORAZÓN de la carga: debes comprender y aconsejar sobre el llenado correcto de **Air Waybill (AWB), Bill of Lading (B/L), Documentos del Camionero, Orden de Entrega (Delivery Order)** y todos los documentos de cumplimiento. "
            "**FORMATO OBLIGATORIO:** Tu respuesta debe ser EXTREMADAMENTE **CORTA, PRECISA, SENCILLA y FÁCIL de ENTENDER**. Limítate generalmente a una o dos oraciones/líneas, máximo tres. Siempre enfócate en soluciones accionables para prevenir Holds, devoluciones o pérdidas. "
            "**ADVERTENCIA DE COSTO (Sólo si es pregunta múltiple):** Si detectas que el usuario ha formulado más de una pregunta en una sola consulta, debes responder brevemente y añadir una nota al final indicando: 'Costo adicional por pregunta múltiple: $2.00 (Facturado como servicio de Consulta Especializada).' "
            "Cubre el cumplimiento regulatorio (IATA, IMDG, ISPM-15, Seguridad, etc.). "
            "Tu rol es solo de consulta experto. Responde en el idioma de la pregunta."
        )

        prompt = f"Consulta específica sobre la carga/logística: {question}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        return {"data": response.text}
    except Exception as e:
        print(f"Error en la llamada a la IA: {e}") 
        return JSONResponse({"error": "Fallo en la conexión con SmartCargo Consulting. Error del servicio."}, status_code=500)

# ------------------ SIMULACION ------------------
@app.get("/simulacion/{tipo}/{count}")
async def run_simulation(tipo: str, count: int):
    riesgo = min(count * 8, 100) 
    sugerencia = "La carga cumple con la mayoría de los requisitos. Riesgo Bajo. Proceso fluido para todos."

    if tipo.lower() in ["dg", "hazmat", "quimicos"] or count > 5:
        riesgo = min(riesgo + 25, 100) 
        sugerencia = "¡CRÍTICO! Múltiples fallas regulatorias detectadas. Riesgo de HOLD y MULTA. ¡Corrección inmediata en etiquetado y documentos!"
    
    elif count >= 3:
        sugerencia = "Inconsistencias detectadas. Recomendamos doble chequeo y validación de embalaje. Evite retrasos innecesarios."

    return {"riesgo_rechazo": f"{riesgo}%", "sugerencia": sugerencia}

# ------------------ OTROS ENDPOINTS (Mocks) ------------------
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    payment_url = f"https://stripe.com/pay/simulated?amount={amount}&desc={description}"
    return {"url": payment_url, "message": "Simulated payment link"}

@app.post("/update-checklist")
async def update_checklist(payload: dict):
    return {"message": "Checklist updated", "data": payload}
