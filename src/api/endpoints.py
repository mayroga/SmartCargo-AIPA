# src/api/endpoints.py

import os
import json
import datetime
from uuid import UUID

from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import stripe

# --- Config & models ---
from src.config.env_keys import (
    STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, BASE_URL,
    ADMIN_USERNAME, ADMIN_PASSWORD, DATABASE_URI, LEGAL_DISCLAIMER_CORE
)
from src.config.price_constants import SERVICE_LEVELS, PRICE_LEGAL_DISCLAIMER_TEXT

from src.db.models.db_setup import Base
from src.db.models.Shipments import Shipment
from src.db.models.Transactions import Transaction
from src.db.models.Reports import Report
from src.db.models.Users import User

# --- Logic ---
from src.logic.measurement import calculate_volumetric_weight, determine_billing_weight
from src.logic.pallet_validator import validate_ispm15_compliance
from src.logic.ia_validator import analyze_photo_and_dg, get_assistant_response
from src.logic.temp_validator import validate_temperature_needs
from src.logic.reporting import generate_pdf_logic
from src.logic.scpam import run_rvd, run_acpf, run_pro, run_psra, generate_rtc_report

from legal.guardrails import PROHIBITED_ACTIONS_DG

# --- App init ---
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Database setup
if not DATABASE_URI:
    raise RuntimeError("DATABASE_URI no configurada en variables de entorno (config/env_keys.py)")

engine = create_engine(DATABASE_URI, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

# Stripe init
stripe.api_key = STRIPE_SECRET_KEY


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


@app.route('/cargo/validate/pallet', methods=['POST'])
def validate_pallet_status():
    payload = request.get_json() or {}
    shipment_id = payload.get('shipment_id')
    is_wood_pallet = payload.get('is_wood_pallet', False)
    pallet_marks = payload.get('pallet_marks', [])

    result = validate_ispm15_compliance(is_wood_pallet, pallet_marks)

    db = SessionLocal()
    try:
        shipment = db.query(Shipment).filter_by(shipment_id=UUID(shipment_id)).first() if shipment_id else None
        if shipment:
            shipment.is_wood_pallet = bool(is_wood_pallet)
            shipment.ispm15_conf = (result.get('risk_level', 5) < 5)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    return jsonify(result), 200


@app.route('/payment/create-checkout', methods=['POST'])
def create_checkout_session():
    data = request.get_json() or {}
    shipment_id = data.get('shipment_id')
    user_id = data.get('user_id')

    tier_key = 'LEVEL_BASIC'
    tier_info = SERVICE_LEVELS.get(tier_key)
    if not tier_info:
        return jsonify({"error": "Tier no disponible"}), 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': tier_info['name'],
                        'description': tier_info['description'],
                    },
                    'unit_amount': int(tier_info['price_usd'] * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{BASE_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&shipment_id={shipment_id}",
            cancel_url=f"{BASE_URL}/payment/cancel?shipment_id={shipment_id}",
            metadata={
                'shipment_id': shipment_id,
                'user_id': user_id,
                'tier_purchased': tier_key
            }
        )
        return jsonify({'id': session.id}), 200
    except Exception as e:
        return jsonify({'error': 'Error al crear la sesión de pago', 'details': str(e)}), 500


@app.route('/payment/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        shipment_id = session['metadata'].get('shipment_id')
        tier_purchased = session['metadata'].get('tier_purchased')

        db = SessionLocal()
        try:
            shipment = db.query(Shipment).filter_by(shipment_id=UUID(shipment_id)).first()
            if shipment:
                new_tx = Transaction(
                    shipment_id=shipment.shipment_id,
                    stripe_session_id=session.get('id'),
                    price_paid=(session.get('amount_total') or 0) / 100.0,
                    status='Completed',
                    tier_purchased=tier_purchased
                )
                db.add(new_tx)
                shipment.status = 'Paid'
                shipment.service_tier = tier_purchased
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    return jsonify({'status': 'success'}), 200


@app.route('/cargo/validate/photo', methods=['POST'])
def validate_photo_and_dg_info():
    shipment_id = request.form.get('shipment_id')
    commodity_description = request.form.get('commodity_description', '')
    image_file = request.files.get('image')

    tmp_path = None
    if image_file:
        tmp_dir = os.path.join('tmp', 'uploads')
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, f"{datetime.datetime.utcnow().timestamp()}_{image_file.filename}")
        image_file.save(tmp_path)

    try:
        validation_result = analyze_photo_and_dg(tmp_path, commodity_description)
    except Exception as e:
        return jsonify({"error": "Error IA", "details": str(e)}), 500

    db = SessionLocal()
    try:
        shipment = db.query(Shipment).filter_by(shipment_id=UUID(shipment_id)).first() if shipment_id else None
        if shipment:
            shipment.dg_risk_keywords = validation_result.get('dg_risk_level')
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    return jsonify({
        "status": "success",
        "ia_advice": validation_result.get('ia_response'),
        "dg_risk": validation_result.get('dg_risk_level'),
        "legal_warning_fixed": LEGAL_DISCLAIMER_CORE
    }), 200


@app.route('/assistant/query', methods=['POST'])
def assistant_query():
    data = request.get_json() or {}
    user_prompt = data.get('prompt', '')
    try:
        response_text = get_assistant_response(user_prompt)
        return jsonify({"response": response_text}), 200
    except Exception as e:
        return jsonify({"error": "IA error", "details": str(e)}), 500


@app.route('/cargo/validate/temperature', methods=['POST'])
def validate_temperature_status():
    data = request.get_json() or {}
    commodity = data.get('commodity', '')
    temp_range = data.get('required_temp_range', [0, 25])
    duration_hours = data.get('duration_hours', 48)
    try:
        validation_result = validate_temperature_needs(commodity, temp_range, duration_hours)
        return jsonify(validation_result), 200
    except Exception as e:
        return jsonify({"error": "Temp validation error", "details": str(e)}), 500


@app.route('/report/generate', methods=['POST'])
def generate_advanced_report():
    data = request.get_json() or {}
    shipment_id = data.get('shipment_id')
    if not shipment_id:
        return jsonify({"error": "shipment_id requerido"}), 400

    db = SessionLocal()
    try:
        shipment = db.query(Shipment).filter_by(shipment_id=UUID(shipment_id)).first()
        if not shipment or shipment.status != 'Paid':
            return jsonify({"error": "Pago no completado. No se puede generar el informe."}), 402

        rvd = run_rvd(shipment)
        acpf = run_acpf(shipment)
        pro = run_pro(shipment)
        psra = run_psra(shipment)

        rtc_payload = {
            "rvd": rvd,
            "acpf": acpf,
            "pro": pro,
            "psra": psra
        }
        pdf_url = generate_pdf_logic(shipment, rtc_payload=rtc_payload, is_advanced=(shipment.service_tier != 'LEVEL_BASIC'))

        new_report = Report(
            shipment_id=shipment.shipment_id,
            pdf_url=pdf_url,
            legal_disclaimer_core=shipment.legal_disclaimer_at_creation,
            legal_disclaimer_price=PRICE_LEGAL_DISCLAIMER_TEXT
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error generando reporte", "details": str(e)}), 500
    finally:
        db.close()

    return jsonify({"status": "Reporte Avanzado Generado", "report_url": pdf_url}), 200


@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USERNAME:
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(username=username).first()
            if user and user.is_admin and password == ADMIN_PASSWORD:
                token = generate_admin_token(str(user.user_id))
                user.last_login_at = datetime.datetime.utcnow()
                db.commit()
                return jsonify({"status": "Login exitoso", "token": token}), 200
        finally:
            db.close()

    return jsonify({"error": "Credenciales de administrador inválidas. Acceso denegado (Regla 3.1)."}), 401


@app.route('/admin/audits', methods=['GET'])
def get_legal_audits():
    db = SessionLocal()
    try:
        reports = db.query(Report).all()
        audit_data = []
        for report in reports:
            audit_data.append({
                "report_id": str(report.report_id),
                "shipment_id": str(report.shipment_id),
                "generated_at": report.generated_at.isoformat(),
                "legal_disclaimer_used": report.legal_disclaimer_core,
                "pdf_url": report.pdf_url
            })
        return jsonify({"status": "success", "total_reports": len(audit_data), "data": audit_data}), 200
    finally:
        db.close()


@app.route('/reports/<path:filename>', methods=['GET'])
def serve_report_file(filename):
    reports_dir = os.path.join(app.static_folder, 'reports')
    return send_from_directory(reports_dir, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
