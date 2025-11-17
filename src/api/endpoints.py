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
        # ... (Importaciones existentes)
from db.models.Transactions import Transaction # Necesitas este modelo
from config.env_keys import STRIPE_WEBHOOK_SECRET
import json

@app.route('/payment/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # 1. Seguridad: Verificar la firma del webhook (Blindaje profesional)
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
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
            # Registrar el pago
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
            
            # En este punto, el cliente puede generar el PDF.
        
    return jsonify({'status': 'success'}), 200


@app.route('/report/generate', methods=['POST'])
def generate_simple_report():
    data = request.json
    shipment_id = data.get('shipment_id')
    
    # 1. Verificar el pago (Blindaje legal)
    shipment = Shipment.query.filter_by(shipment_id=shipment_id).first()
    if not shipment or shipment.status != 'Paid':
        return jsonify({"error": "Pago no completado. No se puede generar el informe legal."}), 402

    # 2. Lógica del Generador de Reporte Básico (Fase 1)
    # Se llama a la lógica para generar el PDF de diagnóstico simple (texto y datos de medición).
    pdf_url = generate_pdf_logic(shipment) # Implementado en logic/reporting.py
    
    # 3. Registrar el informe en la Base de Datos (Modelo Reports)
    # Se registra el link del PDF y el mensaje legal fijo usado.
    new_report = Report(
        shipment_id=shipment_id,
        pdf_url=pdf_url,
        # Se registra el descargo legal que se usó en el PDF
        legal_disclaimer_core=shipment.legal_disclaimer_at_creation, 
        legal_disclaimer_price=PRICE_LEGAL_DISCLAIMER_TEXT 
    )
    db.session.add(new_report)
    db.session.commit()
    
    return jsonify({"status": "Reporte generado", "report_url": pdf_url})
B. Modelo de Datos Fijo: db/models/Reports.py y db/models/Transactions.py
Necesitas estos dos modelos para que los endpoints anteriores funcionen correctamente y garanticen la auditoría legal.

Python

# SMARTCARGO-AIPA/db/models/Transactions.py

# ... (Importaciones necesarias: SQLAlchemy, UUID, etc.)

class Transaction(Base):
    """Modelo para registrar pagos fijos (Stripe)."""
    __tablename__ = 'transactions'
# SMARTCARGO-AIPA/src/api/endpoints.py (ADICIÓN AL ARCHIVO EXISTENTE)

# ... (Importaciones existentes, ahora incluir: from src.logic.ia_validator import analyze_photo_and_dg, get_assistant_response)


# ==============================================================================
# 4. ENDPOINT: Validación Fotográfica y DG Informativa
# Corresponde al Endpoint /cargo/validate/photo
# ==============================================================================
@app.route('/cargo/validate/photo', methods=['POST'])
def validate_photo_and_dg_info():
    # Asume que el archivo de imagen se recibe junto con los metadatos
    shipment_id = request.form.get('shipment_id')
    commodity_description = request.form.get('commodity_description')
    image_file = request.files.get('image') # Archivo de imagen subido

    # 1. Guardar la imagen temporalmente (o subirla a almacenamiento)
    # image_path = save_temp_image(image_file) 
    
    # 2. Análisis de IA (6.4, 6.5)
    validation_result = analyze_photo_and_dg(image_file, commodity_description)
    
    # 3. Registrar el resultado de riesgo DG en la DB (para auditoría)
    shipment = Shipment.query.filter_by(shipment_id=shipment_id).first()
    if shipment:
        shipment.dg_risk_keywords = validation_result['dg_risk_level'] # Almacenar el nivel de riesgo
        # db.session.commit()
    
    # 4. Devolver la respuesta de la IA y el blindaje legal
    return jsonify({
        "status": "success",
        "ia_advice": validation_result['ia_response'],
        "dg_risk": validation_result['dg_risk_level'],
        "warning": "⚠️ Esto puede estar regulado. " + validation_result['legal_warning_fixed']
    })


# ==============================================================================
# 5. ENDPOINT: Asistente Inteligente (Chat)
# Corresponde al Endpoint /assistant/query
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
# SMARTCARGO-AIPA/src/api/endpoints.py (ADICIÓN AL ARCHIVO EXISTENTE)

# ... (Importaciones existentes, agregar: from src.logic.temp_validator import validate_temperature_needs)
# ... (Necesitas la función generate_pdf_logic en src/logic/reporting.py)

# ==============================================================================
# 6. ENDPOINT: Validación de Temperatura
# Corresponde al Endpoint /cargo/validate/temperature
# ==============================================================================
@app.route('/cargo/validate/temperature', methods=['POST'])
def validate_temperature_status():
    data = request.json
    commodity = data.get('commodity')
    temp_range = data.get('required_temp_range', [0, 25]) # Rango [min, max]
    duration_hours = data.get('duration_hours', 48)

    validation_result = validate_temperature_needs(commodity, temp_range, duration_hours)
    
    # Aquí se puede actualizar el registro del envío (ej. 'shipment.temp_data = validation_result')
    
    return jsonify(validation_result)

# ==============================================================================
# 7. ENDPOINT: Generador de Informes (PDF Avanzado)
# Corresponde al Endpoint /report/generate (Ahora maneja Fase 3)
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
    # Esta lógica consolida: Medición, Pallets, IA (DG/Foto) y Temperatura.
    pdf_url = generate_pdf_logic(shipment, is_advanced=(shipment.service_tier != 'LEVEL_BASIC'))
    
    # 3. Registrar el informe en la Base de Datos (Modelo Reports)
    # Se utiliza el texto legal FIJO almacenado en el envío y la configuración.
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
    
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipments.shipment_id'), nullable=False)
    stripe_session_id = Column(String(255), nullable=False)
    price_paid = Column(Float, nullable=False)
    status = Column(String(50), nullable=False) # Completed, Failed, Pending
    tier_purchased = Column(String(50), nullable=False) # LEVEL_BASIC (Fase 1)
    transaction_date = Column(DateTime, default=datetime.datetime.utcnow)
        return jsonify({'id': session.id})
    except Exception as e:
        # Esto es crítico para el blindaje profesional
        print(f"Stripe Error: {e}")
        return jsonify({'error': 'Error al crear la sesión de pago.'}), 500
