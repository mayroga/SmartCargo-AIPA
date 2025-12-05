# src/api/endpoints.py

import os
import json
import datetime
from uuid import UUID

from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import stripe

# --- Config & constants ---
from config.env_keys import (
    STRIPE_API_KEY,
    STRIPE_WEBHOOK_SECRET,
    DATABASE_URI,
    BASE_URL,
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    EMAIL_API_KEY
)

from config.price_constants import SERVICE_LEVELS, PRICE_LEGAL_DISCLAIMER_TEXT

from db.models.db_setup import Base
from db.models.Shipments import Shipment
from db.models.Transactions import Transaction
from db.models.Reports import Report
from db.models.Users import User

# --- Logic ---
from logic.measurement import calculate_volumetric_weight, determine_billing_weight
from logic.pallet_validator import validate_ispm15_compliance
from logic.ia_validator import analyze_photo_and_dg, get_assistant_response
from logic.temp_validator import validate_temperature_needs
from logic.reporting import generate_pdf_logic
from logic.scpam import run_rvd, run_acpf, run_pro, run_psra, generate_rtc_report

from requirements.legal.guardrails import PROHIBITED_ACTIONS_DG

# --- App init ---
app = Flask(__name__, static_folder='static', static_url_path='/static')

# --- Legal disclaimer profesional ---
LEGAL_DISCLAIMER_CORE = (
    "Aviso Legal: Toda mercancía enviada a través de este sistema debe cumplir con la normativa "
    "vigente de transporte internacional y regulaciones de materiales peligrosos. "
    "El usuario es responsable de declarar correctamente los productos y aceptar las condiciones de riesgo. "
    "Este sistema no se hace responsable por sanciones o pérdidas derivadas del incumplimiento de la ley."
)

# --- Database setup ---
if not DATABASE_URI:
    raise RuntimeError("DATABASE_URI no configurada en variables de entorno (config/env_keys.py)")

engine = create_engine(DATABASE_URI, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

# --- Stripe init ---
stripe.api_key = STRIPE_API_KEY


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_admin_token(user_id):
    return f"admin_token_{user_id}_{int(datetime.datetime.utcnow().timestamp())}"


# ===================== Endpoints =====================

@app.route('/cargo/measurements', methods=['POST'])
def process_measurement_and_register():
    data = request.get_json() or {}
    l = data.get('length')
    w = data.get('width')
    h = data.get('height')
    real_weight = data.get('real_weight')
    unit = data.get('unit', 'CM')
    commodity_type = (data.get('commodity_type') or '').upper()

    if any(keyword in commodity_type for keyword in ["BATERÍA", "LITHIUM", "EXPLOSIVO", "QUÍMICO", "AEROSOL", "PINTURA"]):
        return jsonify({
            "error": "Riesgo DG detectado",
            "message": "Advertencia: El sistema no puede proceder con productos de riesgo evidente. " + LEGAL_DISCLAIMER_CORE
        }), 403

    try:
        vol_weight = calculate_volumetric_weight(l, w, h, unit)
        billing_weight = determine_billing_weight(real_weight, vol_weight)
    except Exception as e:
        return jsonify({"error": "Error en cálculos de medidas", "details": str(e)}), 400

    db = SessionLocal()
    try:
        new_shipment = Shipment(
            client_id=data.get('user_id'),
            length_cm=l, width_cm=w, height_cm=h,
            weight_real_kg=real_weight,
            shipper_name=data.get('shipper_name'),
            consignee_name=data.get('consignee_name'),
            airport_code=data.get('airport_code'),
            commodity_type=commodity_type,
            legal_disclaimer_at_creation=LEGAL_DISCLAIMER_CORE,
            status="PENDING"
        )
        db.add(new_shipment)
        db.commit()
        db.refresh(new_shipment)
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error al registrar envío", "details": str(e)}), 500
    finally:
        db.close()

    return jsonify({
        "status": "success",
        "shipment_id": str(new_shipment.shipment_id),
        "billing_weight": billing_weight,
        "action": "Proceed to Pricing/Checkout"
    }), 201

# --- Aquí irían los demás endpoints (pallet, payment, webhook, assistant, temperature, report, admin login) ---
# Se pueden copiar directamente de tu versión anterior, usando LEGAL_DISCLAIMER_CORE
# y las variables importadas desde config.env_keys

# --- App run ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
