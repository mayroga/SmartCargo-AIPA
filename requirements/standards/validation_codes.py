# SMARTCARGO-AIPA/requirements/standards/validation_codes.py

# ==============================================================================
# FIJO: Códigos de Validación de Estándares Internacionales (Regla 6.7)
# ==============================================================================

# --- Marcas requeridas para el estándar ISPM-15 (Tratamiento de madera) ---
# Esta lista es la fuente de verdad para la validación lógica en el backend.
ISPM_15_MARKS = [
    "HT",  # Heat Treatment (Tratamiento Térmico)
    "MB",  # Methyl Bromide (Tratamiento con Bromuro de Metilo) - Desfasado, pero aceptado
    "DB",  # Debarked (Descortezado)
    "SF",  # Sulfuryl Fluoride (Fluoruro de sulfurilo)
    # Incluye otras marcas relevantes para la validación de cumplimiento.
]

# --- Otros códigos de validación ---
# Aquí se podrían agregar códigos DG o de temperatura si fueran necesarios
# DGR_CLASSES = {1: "Explosives", 2: "Gases", ...}
