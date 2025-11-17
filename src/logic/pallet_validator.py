# SMARTCARGO-AIPA/src/logic/pallet_validator.py

from requirements.standards.validation_codes import ISPM_15_MARKS 

# Códigos Fijos (HT, Fumigación, Timbre)
ISPM_15_MARKS = ["HT", "Fumigación certificada", "Timbre oficial internacional"]

def validate_ispm15_compliance(is_wood_pallet, user_declared_marks):
    """
    Verifica el cumplimiento de la norma ISPM-15 y determina el riesgo de rechazo.
    """
    if not is_wood_pallet:
        # Si no es madera (plástico, cartón), el riesgo de rechazo por plaga es 0.
        return {"risk_level": 0, "status": "No Aplica (Pallet Alternativo)", "warning": None}

    # Si es madera, debe tener al menos una marca obligatoria.
    has_required_mark = any(mark in user_declared_marks for mark in ISPM_15_MARKS)
    
    if has_required_mark:
        return {
            "risk_level": 1, 
            "status": "Cumple (ISPM-15 declarado)", 
            "warning": "Recomendamos verificar que el sello esté visible antes de la entrega."
        }
    else:
        # Esto dispara las consecuencias fijas (rechazo, multa, demora)
        critical_warning = (
            "❌ CRÍTICO: El pallet de madera no tiene sello ISPM-15 visible. "
            "Esto puede resultar en RECHAZO, RETORNO, MULTAS y DEMORAS. "
            "Recomendamos reemplazar o confirmar certificación urgente."
        )
        return {
            "risk_level": 5, 
            "status": "Incumplimiento Crítico", 
            "warning": critical_warning
        }
