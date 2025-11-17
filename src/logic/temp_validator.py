# SMARTCARGO-AIPA/src/logic/temp_validator.py

# --- RANGOS Y RECOMENDACIONES TÉRMICAS FIJAS ---
TEMP_STANDARDS = {
    "CARNES": {"range": [-2.0, 4.0], "recommendation": ["Gel packs eutécticos", "Neveras pasivas certificadas", "Camión refrigerado (sugerencia)"]},
    "FLORES": {"range": [2.0, 8.0], "recommendation": ["Gel packs de retención", "Manta térmica protectora", "Prioridad de rampa"]},
    "VACUNAS": {"range": [2.0, 8.0], "recommendation": ["Dry Ice (declarado)", "PCM (Phase Change Materials)", "Contenedor activo (sugerencia)"]},
    "QUIMICOS": {"range": [10.0, 25.0], "recommendation": ["Acondicionamiento simple", "Monitoreo de temperatura (GPS)"]},
    # Asegurar que DRY ICE solo se sugiera si es relevante, y debe ser declarado
}

def validate_temperature_needs(commodity, required_temp_range, duration_hours):
    """
    Evalúa el producto y la duración para sugerir soluciones térmicas (6.6).
    """
    commodity_upper = commodity.upper()
    
    # 1. Chequeo de producto sensible
    if not any(key in commodity_upper for key in TEMP_STANDARDS.keys()):
        return {"status": "No sensible", "recommendations": ["No requiere control activo de temperatura."]}

    # 2. Obtener recomendaciones específicas
    for key, data in TEMP_STANDARDS.items():
        if key in commodity_upper:
            # Añadir sugerencia de 'Dry Ice Declarado' si aplica y la duración es larga (blindaje 8.0)
            recos = list(data["recommendation"])
            if "Dry Ice (declarado)" in recos and duration_hours > 24:
                recos.append("ADVERTENCIA: Dry Ice debe ser declarado obligatoriamente (Sección 8).")
            
            return {
                "status": "Sensible detectado",
                "temp_range_ideal": data["range"],
                "recommendations": recos
            }

    return {"status": "No clasificado", "recommendations": ["Consulte a un experto en cadena de frío."]}
