from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Any, Dict, List
import stripe
import os
import json
import asyncpg
import base64
import asyncio

# ---------------------------------------------------------
# INIT FASTAPI
# ---------------------------------------------------------
app = FastAPI(
    title="SmartCargo-AIPA Backend",
    description="Asistencia Inteligente Profesional para Carga Aérea y Marítima — AIPA Advisory Mode Only (No TSA, No Certificaciones).",
    version="1.0.0",
)

# ---------------------------------------------------------
# CORS CONFIG
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Ajustable si deseas limitarlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# DATABASE CONNECTION (Render ENV VAR: DATABASE_URL)
# ---------------------------------------------------------
DB_URL = os.getenv("DATABASE_URL")

async def connect_db():
    try:
        return await asyncpg.connect(DB_URL)
    except Exception as e:
        print("Error connecting to DB:", e)
        return None

# ---------------------------------------------------------
# STRIPE CONFIG (Render ENV VAR: STRIPE_SECRET_KEY)
# ---------------------------------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ---------------------------------------------------------
# UTILITY: STANDARD RESPONSE
# ---------------------------------------------------------
def success(message: str, data: Any = None):
    return {"status": "success", "message": message, "data": data}

def error(message: str, code: int = 400):
    raise HTTPException(status_code=code, detail=message)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------
@app.get("/")
async def root():
    return success("SmartCargo-AIPA Backend está ONLINE y en modo Asesoría Profesional.")


# ---------------------------------------------------------
# FILE UPLOAD — Ej: imágenes, documentos de carga, fotos
# ---------------------------------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        encoded = base64.b64encode(content).decode("utf-8")

        return success(
            "Archivo recibido correctamente.",
            {
                "filename": file.filename,
                "content_type": file.content_type,
                "base64": encoded[:200] + "..."  # No enviar completo (seguridad)
            }
        )
    except Exception as e:
        return error(f"Error al procesar archivo: {str(e)}")


# ---------------------------------------------------------
# JSON ADVISORY — Asesoría inteligente cargo
# ---------------------------------------------------------
@app.post("/advisory")
async def advisory(data: Dict[str, Any]):
    """
    Recibe datos de carga y devuelve una asesoría técnica profesional.
    """
    try:
        # Aquí puedes expandir la lógica
        response = {
            "analisis": "Asesoría preliminar generada.",
            "recomendaciones": [
                "Verificar documentación comercial.",
                "Confirmar clasificación correcta según la IATA vigente.",
                "Revisar embalaje, peso bruto y neto.",
                "Asegurar que el shipper declaration sea coherente.",
            ],
            "nota_legal": "SmartCargo-AIPA solo proporciona asesoría. No certifica, no valida y no reemplaza requisitos TSA ni regulatorios."
        }

        return success("Asesoría generada.", response)

    except Exception as e:
        return error(f"Error generando asesoría: {e}")


# ---------------------------------------------------------
# STRIPE PAYMENT LINK — Paga y accede a servicios premium
# ---------------------------------------------------------
@app.post("/create-payment")
async def create_payment(amount: int = Form(...), description: str = Form(...)):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": description},
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://smartcargo-advisory.onrender.com/success",
            cancel_url="https://smartcargo-advisory.onrender.com/cancel",
        )

        return success("Pago iniciado.", {"url": session.url})

    except Exception as e:
        return error(f"Stripe error: {str(e)}", 500)


# ---------------------------------------------------------
# DB SAVE ANALYSIS
# ---------------------------------------------------------
@app.post("/save-analysis")
async def save_analysis(
    client_name: str = Form(...),
    cargo_json: str = Form(...),
    advisory_json: str = Form(...)
):

    try:
        conn = await connect_db()
        if not conn:
            return error("No se pudo conectar con la base de datos.", 500)

        await conn.execute(
            """
            INSERT INTO advisory_reports (client_name, cargo_json, advisory_json)
            VALUES ($1, $2, $3);
            """,
            client_name,
            cargo_json,
            advisory_json
        )

        await conn.close()
        return success("Reporte guardado correctamente.")

    except Exception as e:
        return error(f"Error guardando datos: {str(e)}")


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------
@app.get("/health")
async def health():
    return success("OK")


# ---------------------------------------------------------
# CUSTOM ERROR HANDLER
# ---------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": str(exc)},
    )
