# SMARTCARGO-AIPA/src/api/endpoints.py

import stripe
import datetime
import os 
from flask import request, jsonify # Asumiendo el uso de Flask o similar

# --- IMPORTACIONES DE CONFIGURACIÓN Y MODELOS FIJOS ---
from config.env_keys import STRIPE_SECRET_KEY, BASE_URL, LEGAL_DISCLAIMER_CORE
from config.price_constants import SERVICE_LEVELS
from db.models.Shipments import Shipment # Tu modelo de base de datos
from db.models.db_setup import db # Objeto de sesión de base de datos

# --- IMPORTACIONES DE LÓGICA FIJA ---
from src.logic.measurement import calculate_volumetric_weight, determine_billing_weight
from src.logic.pallet_validator import validate_ispm15_compliance
from requirements.legal.guardrails import PROHIBITED_ACTIONS_DG

# Inicialización de Stripe (usando la clave secreta fija)
stripe.api_key = STRIPE_SECRET_KEY 


# ==============================================================================
# 1. ENDPOINT: Medición Inteligente y Registro (Medición, AWB, Guardia DG)
# Corresponde al Endpoint /cargo/measurements
# ==============================================================================
@app.route('/cargo/measurements', methods=['POST'])
def process_measurement_and_register():
    data = request.json
    
    # Datos requeridos para Medición Fija (6.1) y AWB (7.0)
    l, w, h = data.get('length'), data.get('width'), data.get('height')
    real_weight = data.get('real_weight')
    unit = data.get('unit', 'CM')
    commodity_type = data.get('commodity_type', '').upper()
    
    # 1. Validación Básica de Riesgo (Guardarraíl DG 3.1)
    # Se usa una verificación simple en MVP (Fase 2 usará la IA)
    if any(keyword in commodity_type for keyword in ["BATERÍA", "EXPLOSIVO", "QUÍMICO", "AEROSOL", "PINTURA"]):
        return jsonify({
            "error": "Riesgo DG detectado",
            "message": "Advertencia: El sistema no puede proceder con productos de riesgo evidente. " + LEGAL_DISCLAIMER_CORE
        }), 403

    # 2. Cálculo de Peso Facturable
    vol_weight = calculate_volumetric_weight(l, w, h, unit)
    billing_weight = determine_billing_weight(real_weight, vol_weight)
    
    # 3. Registrar Nuevo Envío (Modelo Shipments)
    try:
        new_shipment = Shipment(
            user_id=data.get('user_id'),
            length_cm=l, 
            width_cm=w,
            height_cm=h,
            weight_real_kg=real_weight,
            shipper_name=data.get('shipper_name'),
            consignee_name=data.get('consignee_name'),
            airport_code=data.get('airport_code'),
            # El campo legal_disclaimer_at_creation se establece por defecto (FIJO)
        )
        db.session.add(new_shipment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error de base de datos al registrar envío.", "details": str(e)}), 500

    return jsonify({
        "status": "success",
        "shipment_id": new_shipment.shipment_id,
        "billing_weight": billing_weight,
        "action": "Proceed to Pricing/Checkout"
    })

# ==============================================================================
# 2. ENDPOINT: Validación de Pallets ISPM-15
# Corresponde al Endpoint /cargo/validate/pallet
# ==============================================================================
@app.route('/cargo/validate/pallet', methods=['POST'])
def validate_pallet_status():
    data = request.json
    shipment_id = data.get('shipment_id')
    is_wood_pallet = data.get('is_wood_pallet', False)
    pallet_marks = data.get('pallet_marks', []) 

    validation_result = validate_ispm15_compliance(is_wood_pallet, pallet_marks)

    # 1. Actualizar el registro de envío (Commit de cumplimiento legal)
    shipment = Shipment.query.filter_by(shipment_id=shipment_id).first()
    if shipment:
        shipment.is_wood_pallet = is_wood_pallet
        shipment.ispm15_conf = (validation_result['risk_level'] < 5) # True solo si no hay Incumplimiento Crítico
        db.session.commit()

    # 2. Devolver el resultado de validación (incluye la advertencia crítica)
    return jsonify(validation_result)

# ==============================================================================
# 3. ENDPOINT: Creación de Sesión de Pago (Stripe Checkout)
# Corresponde al Endpoint /payment/create-checkout
# ==============================================================================
@app.route('/payment/create-checkout', methods=['POST'])
def create_checkout_session():
    data = request.json
    shipment_id = data.get('shipment_id')
    user_id = data.get('user_id')
    
    # FASE 1 MVP: SOLO PERMITIMOS EL NIVEL BÁSICO FIJO
    tier_key = 'LEVEL_BASIC'
    tier_info = SERVICE_LEVELS[tier_key]
    
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
                    'unit_amount': int(tier_info['price_usd'] * 100), # Precio fijo: $35.00 (convertido a centavos)
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
        return jsonify({'id': session.id})
    except Exception as e:
        # Esto es crítico para el blindaje profesional
        print(f"Stripe Error: {e}")
        return jsonify({'error': 'Error al crear la sesión de pago.'}), 500
