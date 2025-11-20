# requirements/standards/validation_codes.py

# ==============================================================================
# SMARTCARGO-AIPA BACKEND - ESTÁNDARES DE VALIDACIÓN Y CÓDIGOS FIJOS
# ==============================================================================

# 1. Códigos ISPM-15 (Tratamiento de Madera)
# Estos códigos identifican el tratamiento de calor (HT) o fumigación (MB) requerido.
ISPM_15_MARKS = ["HT", "MB", "DB"]

# 2. Tipos de Carga Peligrosa (DG) para Filtro Básico de IA
# Usados para el primer nivel de advertencia.
DG_KEYWORDS = [
    "BATTERY", "LITHIUM", "EXPLOSIVE", "GAS", "FLAMMABLE", 
    "AEROSOL", "CHEMICAL", "CORROSIVE", "PAINT", "DRY ICE", 
    "RADIOACTIVE", "MAGNETIZED"
]

# 3. Matriz de Incompatibilidad (Simplificada) - **CORRECCIÓN**
# Define qué clases de riesgo DG son incompatibles entre sí para advertir al usuario.
# Esto es una simplificación educativa, no una matriz IATA formal.
INCOMPATIBLE_RISKS = {
    "CLASS_1_EXPLOSIVES": ["FLAMMABLE", "GAS", "ACID"], # Ejemplo
    "CLASS_3_FLAMMABLES": ["EXPLOSIVES", "OXIDIZER", "CORROSIVE"], 
    "CLASS_8_CORROSIVES": ["EXPLOSIVES", "FLAMMABLES", "WATER_REACTIVE"],
    "CLASS_9_MISC": ["EXPLOSIVES"]
}

# 4. Códigos de Aeropuerto IATA (Ejemplo)
AIRPORT_CODES_EXAMPLE = ["LAX", "JFK", "MIA", "MAD", "PEK"]
