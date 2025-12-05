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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY no configurada. /advisory no funcionará correctamente.")

# =====================================================
# MOCK DATABASE Y REGLAS DE NEGOCIO
# =====================================================
cargas_db = []
documents_db = []
alertas_db = []
alertas_count = 0

# BASE DE DATOS DE REGLAS (MÓDULO CENTRAL DE ACTUALIZACIÓN)
# Estas reglas se disparan al crear o actualizar una carga.
rules_db = [
    {"rule_id": "R001", "source": "IATA", "category": "DG", "severity": "CRITICAL", "message_es": "Falta etiqueta de Manejo DG (IATA 5.2.1).", "message_en": "Missing DG Handling Label (IATA 5.2.1)."},
    {"rule_id": "R002", "source": "ISPM15", "category": "Pallet", "severity": "CRITICAL", "message_es": "Pallet de madera sin certificación ISPM-15.", "message_en": "Wooden pallet without ISPM-15 certification."},
    {"rule_id": "R003", "source": "Aerolínea", "category": "Embalaje", "severity": "WARNING", "message_es": "Altura excede el máximo permitido (180cm). Riesgo de rechazo.", "message_en": "Height exceeds maximum allowed (180cm). Risk of rejection."},
    {"rule_id": "R004", "source": "Compatibilidad", "category": "Mercancía", "severity": "CRITICAL", "message_es": "Mercancía DG incompatible con alimentos/perecederos.", "message_en": "DG goods incompatible with food/perishables."},
    {"rule_id": "R005", "source": "Documentos", "category": "AWB", "severity": "WARNING", "message_es": "AWB, Packing List y Peso NO concuerdan (Inconsistencia).", "message_en": "AWB, Packing List and Weight DO NOT match (Inconsistency)."},
]

# =====================================================
# FUNCIONES DE LÓGICA DE AIPA
# =====================================================
def validate_cargo(carga_data):
    """Ejecuta el Motor de Reglas de AIPA (Simulación)."""
    global alertas_count
    generated_alerts = []
    
    # 1. Simulación de Validación de Reglas R001-R005
    tipo_carga = carga_data.get("tipo_carga", "").lower()
    
    # Simulación de Incompatibilidad (R004)
    if tipo_carga == "quimicos" or tipo_carga == "dg":
        if carga_data.get("inconsistencias", 0) > 4: # Más de 4 errores = CRITICAL DG
            rule = next((r for r in rules_db if r["rule_id"] == "R004"), None)
            if rule:
                alertas_count += 1
                generated_alerts.append({"id": str(uuid.uuid4()), "carga_id": carga_data["id"], "mensaje": rule["message_es"], "nivel": rule["severity"], "fecha": str(datetime.utcnow())})
                
    # Simulación de Pallet (R002)
    if carga_data.get("pallet_type", "madera") == "madera" and not carga_data.get("ispm15_verified", False):
        rule = next((r for r in rules_db if r["rule_id"] == "R002"), None)
        if rule:
            alertas_count += 1
            generated_alerts.append({"id": str(uuid.uuid4()), "carga_id": carga_data["id"], "mensaje": rule["message_es"], "nivel": rule["severity"], "fecha": str(datetime.utcnow())})

    # Simulación de Altura (R003)
    if carga_data.get("height_cm", 0) > 180:
        rule = next((r for r in rules_db if r["rule_id"] == "R003"), None)
        if rule:
            alertas_count += 1
            generated_alerts.append({"id": str(uuid.uuid4()), "carga_id": carga_data["id"], "mensaje": rule["message_es"], "nivel": rule["severity"], "fecha": str(datetime.utcnow())})

    # Añadir las alertas generadas a la base de datos global
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
    
    # Simulación de datos extraídos/ingresados
    payload["inconsistencias"] = 0 # Se incrementa con la subida de documentos
    payload["pallet_type"] = payload.get("pallet_type", "madera")
    payload["ispm15_verified"] = payload.get("ispm15_verified", False)
    payload["height_cm"] = payload.get("height_cm", 150)
    
    # Ejecutar el motor de reglas
    validated_carga = validate_cargo(payload)
    
    cargas_db.append(validated_carga)
    return {"id": carga_id, "alertas": validated_carga["alertas"]}

# ------------------ DOCUMENTOS ------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), carga_id: str = Form("N/A")):
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"uploads/{filename}"
    os.makedirs("uploads", exist_ok=True)
    
    # Guardar archivo (simulado)
    # with open(file_path, "wb") as f:
    #     f.write(await file.read())
        
    # **AQUÍ: Simulación de Verificación de Documentos (R005)**
    if "invoice" in filename.lower() and carga_id == "SC-AIPA-TEST-01":
        # Dispara una alerta de inconsistencia para la carga de prueba
        alerta = next((r for r in rules_db if r["rule_id"] == "R005"), None)
        if alerta:
            global alertas_count
            alertas_count += 1
            alertas_db.append({"id": str(uuid.uuid4()), "carga_id": carga_id, "mensaje": alerta["message_es"], "nivel": alerta["severity"], "fecha": str(datetime.utcnow())})
    
    documents_db.append({"id": str(uuid.uuid4()), "filename": filename, "carga_id": carga_id, "fecha_subida": str(datetime.utcnow())})
    
    return {"data": {"filename": filename, "carga_id": carga_id}}

# ------------------ ALERTAS ------------------
@app.get("/alertas")
async def get_alertas():
    # Ordenar las alertas por nivel (CRITICAL primero)
    sorted_alertas = sorted(alertas_db, key=lambda a: a['nivel'], reverse=True)
    return {"alertas": sorted_alertas}

# ------------------ ADVISORY (GEMINI) ------------------
@app.post("/advisory")
async def advisory(question: str = Form(...)):
    if not GEMINI_API_KEY:
        return JSONResponse({"error":"GEMINI_API_KEY no configurada. Asesoría IA inactiva."}, status_code=500)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        system_instruction = (
            "Eres SmartCargo-AIPA, un asesor logístico experto. Proporcionas asesoramiento preventivo basado en regulaciones de carga "
            "(IATA DG, TSA, ISPM-15, reglas de aerolíneas). Tu misión es cubrir todos los episodios de la vida de la carga. "
            "Nunca asumes responsabilidad legal ni emites certificaciones. Responde de manera concisa y profesional en español."
        )

        prompt = f"Consulta sobre carga: {question}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        return {"data": response.text}
    except Exception as e:
        print(f"Error en la llamada a Gemini: {e}")
        return JSONResponse({"error": "Fallo en la conexión con la IA de asesoría. Error del servicio."}, status_code=500)

# ------------------ SIMULACION ------------------
@app.get("/simulacion/{tipo}/{count}")
async def run_simulation(tipo: str, count: int):
    # Predicción de rechazo (Sección 3.5)
    
    riesgo = min(count * 8, 100) # 8% de riesgo por cada inconsistencia (count)
    sugerencia = "La carga parece cumplir con los requisitos básicos."

    if tipo.lower() in ["dg", "hazmat", "quimicos"]:
        riesgo = min(riesgo + 25, 100) # Alto riesgo base para DG
        sugerencia = "Revisión urgente de la Declaración DG y el etiquetado. Alto riesgo de rechazo."
    
    if riesgo > 50:
        sugerencia = "Alto riesgo. Sugerencia: Reempaque inmediato y verificación de ISPM-15."

    return {"riesgo_rechazo": f"{riesgo}%", "sugerencia": sugerencia}

# ------------------ OTROS ENDPOINTS (Mocks) ------------------
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    payment_url = f"https://stripe.com/pay/simulated?amount={amount}&desc={description}"
    return {"url": payment_url, "message": "Simulated payment link"}

@app.post("/update-checklist")
async def update_checklist(payload: dict):
    return {"message": "Checklist updated", "data": payload}
