from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, stripe, psycopg2, datetime, json

# -------- CONFIGURACIÓN GLOBAL SEGURA -------- #
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
DATABASE_URI = os.environ.get("DATABASE_URI")

conn = psycopg2.connect(DATABASE_URI)
cur = conn.cursor()

app = FastAPI(title="SmartCargo-AIPA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- MODELOS -------- #
class Carga(BaseModel):
    cliente: str
    tipo: str
    estado: str
    alertas: int

class Pregunta(BaseModel):
    pregunta: str

# -------- FUNCIONES INTERNAS -------- #
def registrar_carga(carga: Carga):
    cur.execute(
        """
        INSERT INTO cargas (cliente,tipo,estado,alertas,fecha_creacion)
        VALUES (%s,%s,%s,%s,%s) RETURNING id
        """,
        (carga.cliente, carga.tipo, carga.estado, carga.alertas, datetime.datetime.now())
    )
    conn.commit()
    return cur.fetchone()[0]

def prediccion_rechazo(tipo, alertas):
    # Sistema de IA SIMPLE simulada (seguro legal)
    riesgo = "Bajo"
    if alertas >= 2: riesgo = "Medio"
    if alertas >= 4: riesgo = "Alto"
    return {
        "tipo": tipo,
        "alertas": alertas,
        "riesgo_rechazo": riesgo,
        "mensaje": f"Riesgo potencial de rechazo: {riesgo}. Esto es asesoría, no certificación."
    }

def analizar_documento(nombre):
    if "awb" in nombre.lower(): return "Air Waybill detectado, listo para revisión."
    if "invoice" in nombre.lower(): return "Factura detectada, validación iniciada."
    if "packing" in nombre.lower(): return "Packing List detectado, comparando cantidades."
    return "Documento general cargado y registrado para asesoría."

# -------- ENDPOINTS PRINCIPALES -------- #

@app.get("/cargas")
def obtener_cargas():
    cur.execute("SELECT * FROM cargas ORDER BY id DESC")
    return {"cargas": cur.fetchall()}

@app.post("/carga")
def crear_carga(carga: Carga):
    id_carga = registrar_carga(carga)
    return {"id": id_carga, "mensaje": "Carga registrada profesionalmente."}

@app.post("/documento")
async def subir_documento(file: UploadFile = File(...)):
    contenido = await file.read()
    nombre = file.filename
    analisis = analizar_documento(nombre)
    return {
        "archivo": nombre,
        "tamano": len(contenido),
        "analisis": analisis,
        "nota_legal": "SmartCargo-AIPA sólo asesora. No valida legalmente documentos."
    }

@app.get("/simulacion/{tipo}/{alertas}")
def simulacion(tipo: str, alertas: int):
    return prediccion_rechazo(tipo, alertas)

@app.post("/asistente")
def asistente_virtual(p: Pregunta):
    respuesta = f"Análisis experto sobre '{p.pregunta}'. Esto es solo asesoría preventiva."
    return {"respuesta": respuesta}

# -------- PAGOS PROFESIONALES -------- #
@app.post("/checkout")
def checkout(data: dict):
    try:
        precio = data["precio"]
        success = data["success"]
        cancel = data["cancel"]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency":"usd",
                    "product_data":{"name":"SmartCargo-AIPA Subscription"},
                    "unit_amount": int(precio * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=success,
            cancel_url=cancel
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(400, str(e))
