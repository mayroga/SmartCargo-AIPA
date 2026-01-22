def generate_semaforo(status):
    """
    Devuelve texto simple que Avianca entiende:
    🟢 LISTA PARA ACEPTACIÓN
    🟡 ACEPTABLE CON RIESGO
    🔴 NO ACEPTABLE
    """
    return status

def cargo_summary(cargo, documents):
    status, reasons = validate_cargo(cargo, documents)
    return {
        "cargo_id": cargo.id,
        "mawb": cargo.mawb,
        "hawb": cargo.hawb,
        "status": status,
        "reasons": reasons
    }
