# SMARTCARGO-AIPA/src/api/endpoints.py

from src.logic.measurement import calculate_volumetric_weight, determine_billing_weight
from requirements.legal.guardrails import PROHIBITED_ACTIONS_DG
# ... (otras importaciones: DB session, Pydantic/Marshmallow schema)

@app.route('/cargo/measurements', methods=['POST'])
def process_measurement_and_register():
    data = request.json
    
    # 1. Validación de Medición (6.1)
    # Se asume una sola caja para el MVP, la lógica de múltiples cajas viene en Fase 2
    l, w, h = data['length'], data['width'], data['height']
    real_weight = data['real_weight']
    unit = data['unit']

    vol_weight = calculate_volumetric_weight(l, w, h, unit)
    billing_weight = determine_billing_weight(real_weight, vol_weight)

    # 2. Validación Básica de Riesgo (Guardarraíl Legal 3.1)
    if any(keyword in data['commodity_type'].upper() for keyword in ["BATERÍA", "EXPLOSIVO", "QUÍMICO"]):
        return jsonify({
            "error": "Riesgo DG detectado",
            "message": "Advertencia: El sistema no puede proceder con productos de riesgo evidente. " + LEGAL_DISCLAIMER_CORE
        }), 403

    # 3. Registrar en la DB (Modelo Shipments)
    # Aquí se registra el envío con el LEGAL_DISCLAIMER_CORE fijo
    new_shipment = Shipment(
        user_id=data['user_id'],
        length_cm=l, 
        weight_real_kg=real_weight,
        # ... (otros campos AWB)
    )
    db.session.add(new_shipment)
    db.session.commit()

    return jsonify({
        "status": "success",
        "shipment_id": new_shipment.shipment_id,
        "billing_weight": billing_weight,
        "action": "Proceed to Pricing/Checkout"
    })
