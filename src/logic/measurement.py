# SMARTCARGO-AIPA/src/logic/measurement.py

# --- CONSTANTE FIJA: Factor de Densidad IATA para Carga Aérea (1:6000) ---
IATA_DENSITY_FACTOR_CM = 6000  

def calculate_volumetric_weight(length, width, height, unit='CM'):
    """
    Calcula el peso volumétrico basado en el estándar IATA.
    Devuelve el peso volumétrico en KG.
    """
    if unit.upper() == 'IN':
        # Conversión: 1 pulgada cúbica = 0.000277778 metros cúbicos
        # Factor IATA en pulgadas cúbicas es 166 (por libra) o 366 (por kg)
        # Usamos 366 (pulgadas a kg) o convertimos a CM para consistencia.
        length = length * 2.54
        width = width * 2.54
        height = height * 2.54

    volume_cubic_cm = length * width * height
    
    # Fórmula: Volumen (cm³) / Factor Fijo (6000)
    vol_weight_kg = volume_cubic_cm / IATA_DENSITY_FACTOR_CM
    return vol_weight_kg

def determine_billing_weight(real_weight_kg, vol_weight_kg):
    """El peso facturable es siempre el mayor (Higher Of)."""
    billing_weight = max(real_weight_kg, vol_weight_kg)
    return billing_weight
