import os
import random
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware
import stripe

load_dotenv()

# --- CONFIGURACIÓN DE FASTAPI Y CORS ---
app = FastAPI(title="SmartCargo-AIPA Backend")

# Permitir CORS para desarrollo y entornos de Render
origins = [
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # El origen del frontend en Render:
    "https://smartcargo-advisory.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE GEMINI Y STRIPE ---
try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        client = genai.Client(api_key=gemini_key)
    else:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

except ValueError as e:
    print(f"WARNING: Gemini client failed to initialize. {e}. Advisory service will not work.")
    client = None
except Exception as e:
    print(f"WARNING: General error initializing Gemini client: {e}. Advisory service will not work.")
    client = None

# Configuración de Stripe
stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
if stripe_secret_key:
    stripe.api_key = stripe_secret_key
else:
    print("WARNING: STRIPE_SECRET_KEY not set. Payment route will use simulation.")


# --- DATABASE SIMULATION (Reglas y Alertas) ---

# Base de datos de Alertas (Motor de Reglas AIPA)
# Descripciones enfocadas en el impacto operativo y las soluciones
ALERTS_DB = {
    "R001": {"msg": "Pallet de madera sin sello ISPM-15.", "desc": "Alto riesgo fitosanitario/aduanero. La carga será DEVUELTA. Requiere pallet HT o cambio a plástico.", "risk": 30},
    "R002": {"msg": "Altura excede límite de ULD estándar (180cm).", "desc": "Riesgo de rechazo por sobredimensión o límite de puerta de avión. Requiere re-paletizado inmediato.", "risk": 20},
    "R003": {"msg": "Embalaje CRÍTICO (Roto/Fuga).", "desc": "Violación TSA/IATA. Rechazo inmediato en rampa. Requiere re-embalaje total y revisión del contenido.", "risk": 50},    
    "R004": {"msg": "Etiquetas DG/Frágil/Orientación Faltantes.", "desc": "Incumplimiento de placarding (TSA/IATA). Riesgo de clasificación errónea en bodega.", "risk": 25},    
    "R005": {"msg": "Segregación DG CRÍTICA (Mezcla con NO DG).", "desc": "Peligro de incompatibilidad química/incendio. Rechazo y posible multa. Separe inmediatamente.", "risk": 45},    
    "R006": {"msg": "Discrepancia de Peso AWB/Físico.", "desc": "Alto riesgo de HOLD, re-facturación y retraso. Verifique y corrija el AWB.", "risk": 20},    
    "R007": {"msg": "Contenido DG requiere documento Shipper's Declaration.", "desc": "Documento obligatorio DG faltante o inconsistente. Causa un HOLD inmediato.", "risk": 35},
    "R008": {"msg": "Altura excede límite de 213 cm (Screening TSA).", "desc": "La carga excede el límite de 7 pies para inspección canina/ETD. Riesgo de deconstrucción y re-paletizado.", "risk": 30},
    "R009": {"msg": "Etiquetas DG/Frío no orientadas hacia afuera.", "desc": "Riesgo de clasificación errónea por personal de muelle. Gire los bultos o reubique etiquetas para visibilidad total.", "risk": 15},
}

# Base de datos de Cargas (Simulación de persistencia)
CARGOS_DB = []


# --- SCHEMAS (Pydantic Models) ---

class CargoInput(BaseModel):
    awb: str
    content: str
    length_cm: float
    width_cm: float
    height_cm: float
    weight_declared: float
    weight_unit: str
    # Checkpoints de la Consola Operacional
    packing_integrity: str
    labeling_complete: str
    ispm15_seal: str
    dg_type: str
    dg_separation: Optional[str] = 'NA'
    weight_match: str

class AdvisoryRequest(BaseModel):
    prompt: str


# --- LÓGICA DE NEGOCIO Y MOTOR DE REGLAS ---

# Umbral de Altura Máxima para Screening (7 pies = 213.36 cm)
TSA_SCREENING_MAX_CM = 213.0 


def calculate_risk_score(alerts: List[str]) -> int:
    """Calcula el puntaje total de riesgo basado en las alertas activas."""
    total_risk = sum(ALERTS_DB[alert]["risk"] for alert in alerts)
    
    # Si hay una alerta de rechazo CRÍTICO (R003 o R005), el score debe ser alto.
    if "R003" in alerts or "R005" in alerts:
        return max(85, total_risk)
        
    return min(total_risk, 99) # Máximo 99%


def validate_cargo(cargo: CargoInput) -> dict:
    """Aplica el Motor de Reglas AIPA cubriendo toda la cadena de suministro."""
        
    active_alerts = []

    # --- 1. Reglas Físicas/Dimensiones y Seguridad Operacional ---
    
    # R002: Altura Excedida (Límite ULD Estándar) 
    if cargo.height_cm > 180.0:
        active_alerts.append("R002")
        
    # R008: Altura Excedida para Screening TSA/Canino (7 pies)
    # CRÍTICO: Las cargas muy altas dificultan la inspección de seguridad en el muelle.
    if cargo.height_cm > TSA_SCREENING_MAX_CM:
        active_alerts.append("R008")
        
    # R001: ISPM-15 
    if cargo.ispm15_seal == "NO":
        active_alerts.append("R001")
        
    # R003: Integridad del Embalaje (Rechazo inmediato)
    if cargo.packing_integrity == "CRITICAL":
        active_alerts.append("R003")
        
    # R006: Discrepancia de Peso (Problema de Counter/Facturación)
    if cargo.weight_match == "NO":
        active_alerts.append("R006")
        
    # --- 2. Reglas DG/Hazmat (Forwarder/Especialista y Handler) ---
    
    is_dg = cargo.dg_type != "NO_DG"
    
    if is_dg:
        # R004: Etiquetado DG/Placarding (Visibilidad y Correcto)
        if cargo.labeling_complete == "NO":
            active_alerts.append("R004")

        # R005: Segregación CRÍTICA (IATA/IMDG)
        if cargo.dg_separation == "MIXED":
            active_alerts.append("R005")
            
        # R007: Documentación (Shipper's Declaration)
        # Esto simula un error del Forwarder en el papeleo legal
        if cargo.labeling_complete == "NO" or "BATERIA" in cargo.content.upper():
             active_alerts.append("R007")

        # R009: Visibilidad (Asumimos que si hay DG, deben ser visibles)
        # Esto simula un error de clasificación del Counter/Vasculero
        # Si la integridad no es OK (cajas deformadas) es difícil ver la etiqueta.
        if cargo.packing_integrity != "OK" and cargo.labeling_complete == "YES":
             active_alerts.append("R009")


    # Calculamos el riesgo
    risk_score = calculate_risk_score(list(set(active_alerts)))

    return {
        "awb": cargo.awb,
        "content": cargo.content,
        "length_cm": cargo.length_cm,
        "width_cm": cargo.width_cm,
        "height_cm": cargo.height_cm,
        "weight_declared": cargo.weight_declared,
        "weight_unit": cargo.weight_unit,
        "alertaScore": risk_score,
        "alerts": list(set(active_alerts))
    }


# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "SmartCargo AIPA Backend Operational"}


@app.post("/cargas")
async def create_cargo_validation(cargo: CargoInput):
    """
    Recibe los datos de la Consola Operacional y aplica el Motor de Reglas AIPA.
    """
    validation_result = validate_cargo(cargo)
    CARGOS_DB.append(validation_result)
    return validation_result


@app.post("/advisory")
async def get_advisory(request: AdvisoryRequest):
    """
    Consulta al Asesor IA (Gemini) para obtener una respuesta profesional centrada en SOLUCIONES.
    """
    if not client:
        raise HTTPException(status_code=503, detail="Gemini client is not initialized. Check GEMINI_API_KEY.")
        
    # 🎯 FILOSOFÍA DE SOLUCIÓN Y ALCANCE EXPANDIDO:
    system_instruction = (
        "Eres SMARTCARGO CONSULTING, el ASESOR PREVENTIVO VIRTUAL y SOLUCIONADOR experto en TODA la cadena de suministro logístico: "
        "desde el *Forwarder* (papeleo legal DG), el *Trucker* (seguridad/embalaje), el *Counter Agent* (clasificación/peso/visibilidad) hasta el *Operador* (carguero/ULD). "
        "Tu única misión es: 1. DIAGNOSTICAR el problema que plantea el usuario y 2. PROPORCIONAR la **SOLUCIÓN CORRECTIVA INMEDIATA** de la forma más **PROFESIONAL, PRECISA y CONCISA** posible. "
        
        "**REGLAS DE RESPUESTA CRÍTICAS:** "
        "1. **SOLUCIÓN PRIMERO:** La respuesta principal DEBE ser el diagnóstico y la SOLUCIÓN MÁS CRÍTICA, simple, clara y accionable en un MÁXIMO de 4 a 5 líneas. "
        "2. **BREVEDAD ESTRICTA:** Evita rodeos, introducción y formalidades innecesarias. Ve directo al grano. "
        "3. **PROFUNDIDAD PRECISA:** Si el usuario tiene dudas o necesita más detalle, proporciona la explicación de apoyo en un párrafo corto separado. "
        "4. **AUTORIDAD Y LEYES:** Siempre MENCIONA la regulación de autoridad (IATA DGR, TSA Screening Limits, ISPM-15, Restricciones Operacionales de Aerolíneas) que respalda la solución."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[request.prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return {"data": response.text}
        
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        raise HTTPException(status_code=500, detail="Error en la consulta al Asesor IA. Verifique su clave de API de Gemini.")


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    awb: str = Form(""),
    is_photo: bool = Form(False)
):
    """
    Simula el proceso de revisión de documentos/fotos por el Asesor IA.
    """
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png", "text/plain"]:
        return {"status": "FAILED", "reason": "Tipo de archivo no soportado para análisis AIPA."}
        
    # --- SIMULACIÓN DE ANÁLISIS ---
    
    if file.content_type == "application/pdf" and random.random() < 0.2:
        return {"status": "ALERT", "reason": "Alerta R007: Posible documento DG incompleto o inconsistente (Revisar Shipper's Declaration)."}

    if is_photo and random.random() < 0.1:
        # R003
        return {"status": "ALERT", "reason": "Alerta R003: La IA detectó posible daño crítico al embalaje en la foto subida. Verificación manual requerida."}
        
    return {"status": "OK", "reason": f"Análisis de {file.filename} completado. Cumplimiento preliminar OK."}


@app.post("/create-payment")
async def create_payment_link(amount: int = Form(...), description: str = Form(...)):
    """
    Simulación de la creación de un enlace de pago real con Stripe (ya no es usado en el frontend, pero se mantiene la ruta).
    """
    if stripe_secret_key:
        payment_url = "https://stripe.com/pay/real_url_goes_here"
        
    else:
        payment_url = f"https://stripe.com/pay/simulated?amount={amount}&desc={description}"
        
    return {"url": payment_url, "message": "Simulated payment link"}


@app.get("/simulacion")
def get_simulation_data():
    """Devuelve la base de datos de cargas simuladas."""
    return CARGOS_DB
