# SMARTCARGO-AIPA/src/api/endpoints.py

import stripe
import datetime
import os
import json
from flask import request, jsonify # Asumiendo el uso de Flask o similar

# --- IMPORTACIONES DE CONFIGURACIÓN Y MODELOS FIJOS ---
from config.env_keys import STRIPE_SECRET_KEY, BASE_URL, LEGAL_DISCLAIMER_CORE, STRIPE_WEBHOOK_SECRET
from config.env_keys import ADMIN_USERNAME, ADMIN_PASSWORD # Credenciales fijas de Fase 4
from config.price_constants import SERVICE_LEVELS, PRICE_LEGAL_DISCLAIMER_TEXT # Importar el texto legal de precio
from db.models.Shipments import Shipment
from db.models.Transactions import Transaction # Importado para Webhook
from db.models.Reports import Report # Importado para Reporte
from db.models.Users import User # Importado para Login Admin
from db.models.db_setup import db # Objeto de sesión de base de datos

# --- IMPORTACIONES DE LÓGICA FIJA ---
from src.logic.measurement import calculate_volumetric_weight, determine_billing_weight
from src.logic.pallet_validator import validate_ispm15_compliance
from src.logic.ia_validator import analyze_photo_and_dg, get_assistant_response # Lógica de IA (Fase 2)
from src.logic.temp_validator import validate_temperature_needs # Lógica de Temperatura (Fase 3)
from src.logic.reporting import generate_pdf_logic # Lógica de Generación de PDF (Placeholder)
from requirements.legal.guardrails import PROHIBITED_ACTIONS_DG

# Inicialización de Stripe (usando la clave secreta fija)
stripe.api_key = STRIPE_SECRET_KEY

# --- Placeholder para funciones no provistas ---
def generate_admin_token(user_id):
    """Placeholder para generación de token de JWT"""
    return f"admin_token_{user_id}_secret"

# Se asume que 'app' (Flask app) está inicializada en otro lugar y se usa aquí con decoradores.

# ==============================================================================
# 1. ENDPOINT: Medición Inteligente y Registro (Medición, AWB, Guardia DG)
# ==============================================================================
@app.route('/cargo/measurements', methods=['POST'])
def process_measurement_and_register():
    data = request.json
    
    l, w, h = data.get('length'), data.get('width'), data.get('height')
    real_weight = data.get('real_weight')
    unit = data.get('unit', 'CM')
    commodity_type = data.get('commodity_type', '').upper()
    
    # 1. Validación Básica de Riesgo (Guardarraíl DG 3.1)
    if any(keyword in commodity_type for keyword in ["BATERÍA", "EXPLOSIVO", "QUÍMICO", "AEROSOL", "PINTURA"]):
        return jsonify({
            "error": "Riesgo DG detectado",
            "message": "Advertencia: El sistema no puede proceder con productos de riesgo evidente. " + LEGAL_DISCLAIMER_CORE
        }), 403

    # 2. Cálculo de Peso Facturable
    vol_weight = calculate_volumetric_weight(l, w, h, unit)
    billing_weight = determine_billing_weight(real_weight, vol_weight)
    
    # 3. Registrar Nuevo Envío
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
            commodity_type=commodity_type # Aseguramos guardar el tipo de mercancía
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
# ==============================================================================
@app.route('/payment/create-checkout', methods=['POST'])
def create_checkout_session():
    data = request.json
    shipment_id = data.get('shipment_id')
    user_id = data.get('user_id')
    
    # FASE 1 MVP: SOLO PERMITIMOS EL NIVEL BÁSICO FIJO (LEVEL_BASIC)
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
                    'unit_amount': int(tier_info['price_usd'] * 100), # Precio fijo: $35.00
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
        print(f"Stripe Error: {e}")
        return jsonify({'error': 'Error al crear la sesión de pago.'}), 500

# ==============================================================================
# 4. ENDPOINT: Stripe Webhook (Confirmación de Pago y Auditoría)
# ==============================================================================
@app.route('/payment/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # 1. Seguridad: Verificar la firma del webhook (Blindaje profesional)
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    # 2. Manejo de Eventos Fijos (Solo Payment Successful)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extraer Metadata Fija
        shipment_id = session.metadata.get('shipment_id')
        tier_purchased = session.metadata.get('tier_purchased')
        
        # 3. Registrar Transacción y Actualizar Envío
        shipment = Shipment.query.filter_by(shipment_id=shipment_id).first()

        if shipment:
            new_transaction = Transaction(
                shipment_id=shipment_id,
                stripe_session_id=session.id,
                price_paid=session.amount_total / 100, # Convertir a USD
                status='Completed',
                tier_purchased=tier_purchased
            )
            db.session.add(new_transaction)
            
            # Marcar el envío como pagado y actualizar el nivel
            shipment.status = 'Paid'
            shipment.service_tier = tier_purchased
            db.session.commit()
            
    return jsonify({'status': 'success'}), 200

# ==============================================================================
# 5. ENDPOINT: Validación Fotográfica y DG Informativa (Fase 2)
# ==============================================================================
@app.route('/cargo/validate/photo', methods=['POST'])
def validate_photo_and_dg_info():
    shipment_id = request.form.get('shipment_id')
    commodity_description = request.form.get('commodity_description')
    image_file = request.files.get('image')

    # 1. Análisis de IA (6.4, 6.5)
    validation_result = analyze_photo_and_dg(image_file, commodity_description)
    
    # 2. Registrar el resultado de riesgo DG en la DB (para auditoría)
    shipment = Shipment.query.filter_by(shipment_id=shipment_id).first()
    if shipment:
        shipment.dg_risk_keywords = validation_result['dg_risk_level']
        db.session.commit()
    
    # 3. Devolver la respuesta de la IA y el blindaje legal
    return jsonify({
        "status": "success",
        "ia_advice": validation_result['ia_response'],
        "dg_risk": validation_result['dg_risk_level'],
        "warning": "⚠️ Esto puede estar regulado. " + validation_result['legal_warning_fixed']
    })

# ==============================================================================
# 6. ENDPOINT: Asistente Inteligente (Chat - Fase 2)
# ==============================================================================
@app.route('/assistant/query', methods=['POST'])
def assistant_query():
    data = request.json
    user_prompt = data.get('prompt')
    
    # 1. Lógica del Asistente con Guardrail Fijo (5.0)
    response_text = get_assistant_response(user_prompt)
    
    # 2. La respuesta ya contiene el LEGAL_DISCLAIMER_CORE fijo
    return jsonify({
        "response": response_text
    })

# ==============================================================================
# 7. ENDPOINT: Validación de Temperatura (Fase 3)
# ==============================================================================
@app.route('/cargo/validate/temperature', methods=['POST'])
def validate_temperature_status():
    data = request.json
    commodity = data.get('commodity')
    temp_range = data.get('required_temp_range', [0, 25])
    duration_hours = data.get('duration_hours', 48)

    validation_result = validate_temperature_needs(commodity, temp_range, duration_hours)
    
    # Aquí se puede actualizar el registro del envío (ej. 'shipment.temp_data = validation_result')
    
    return jsonify(validation_result)

# ==============================================================================
# 8. ENDPOINT: Generador de Informes (PDF Avanzado - Fase 3)
# ==============================================================================
@app.route('/report/generate', methods=['POST'])
def generate_advanced_report():
    data = request.json
    shipment_id = data.get('shipment_id')
    
    shipment = Shipment.query.filter_by(shipment_id=shipment_id).first()
    
    # 1. VERIFICACIÓN DE PAGO (Blindaje legal)
    if not shipment or shipment.status != 'Paid':
        return jsonify({"error": "Pago no completado. No se puede generar el informe legal avanzado."}), 402

    # 2. Lógica del Generador de Reporte AVANZADO (10.0)
    pdf_url = generate_pdf_logic(shipment, is_advanced=(shipment.service_tier != 'LEVEL_BASIC'))
    
    # 3. Registrar el informe en la Base de Datos (Modelo Reports)
    new_report = Report(
        shipment_id=shipment_id,
        pdf_url=pdf_url,
        legal_disclaimer_core=shipment.legal_disclaimer_at_creation, 
        legal_disclaimer_price=PRICE_LEGAL_DISCLAIMER_TEXT 
        # Añadir todos los resultados de DG, Pallets, y Temp para auditoría
    )
    db.session.add(new_report)
    db.session.commit()
    
    return jsonify({"status": "Reporte Avanzado Generado", "report_url": pdf_url})

# ==============================================================================
# 9. ENDPOINT: Autenticación de Administración y Acceso a Auditoría (Fase 4)
# ==============================================================================
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # 1. VERIFICACIÓN DE CREDENCIALES FIJAS (Blindaje de entorno)
    if username == ADMIN_USERNAME:
        user = User.query.filter_by(username=username).first()
        
        # Usando la verificación simple con ENV (debería ser hash en prod)
        if user and password == ADMIN_PASSWORD: 
            # 2. Generar token de acceso para auditoría
            access_token = generate_admin_token(user.user_id)
            user.last_login_at = datetime.datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                "status": "Login exitoso",
                "token": access_token
            })
        
    return jsonify({"error": "Credenciales de administrador inválidas. Acceso denegado (Regla 3.1)."}, 401)


# ==============================================================================
# 10. ENDPOINT: Acceso a Registros Legales (Auditoría - Fase 4)
# ==============================================================================
@app.route('/admin/audits', methods=['GET'])
# Se asume una función de seguridad 'require_admin_auth' aquí
# @require_admin_auth 
def get_legal_audits():
    
    # 1. Recuperar todos los registros de Reports (donde están los descargos legales fijos)
    reports = Report.query.all()
    
    audit_data = []
    for report in reports:
        # Se exponen solo los campos críticos para la auditoría legal
        audit_data.append({
            "report_id": str(report.report_id),
            "shipment_id": str(report.shipment_id),
            "generated_at": report.generated_at.isoformat(),
            "legal_disclaimer_used": report.legal_disclaimer_core,
            "pdf_url": report.pdf_url
        })
        
    return jsonify({
        "status": "success",
        "total_reports": len(audit_data),
        "data": audit_data
    })
