# SMARTCARGO-AIPA/src/api/endpoints.py (Fragmento de la función de checkout)

from config.env_keys import STRIPE_SECRET_KEY, BASE_URL
from config.price_constants import SERVICE_LEVELS
import stripe

stripe.api_key = STRIPE_SECRET_KEY

@app.route('/payment/create-checkout', methods=['POST'])
def create_checkout_session():
    data = request.json
    shipment_id = data.get('shipment_id')
    user_id = data.get('user_id')
    
    # FASE 1 MVP: SOLO PERMITIMOS EL NIVEL BÁSICO
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
        # Esto es crítico para el blindaje profesional
        print(f"Stripe Error: {e}")
        return jsonify({'error': 'Error al crear la sesión de pago.'}), 500
