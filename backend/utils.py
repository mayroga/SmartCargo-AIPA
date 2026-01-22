from backend.rules import validate_cargo

def generate_semaforo(status):
    """Convierte status a semáforo operativo"""
    return status

def cargo_summary(cargo, documents, role):
    """
    Retorna info específica según el rol
    """
    status, reasons = validate_cargo(cargo, documents)

    if role == "dueño":
        return {
            "cargo_id": cargo.id,
            "mawb": cargo.mawb,
            "hawb": cargo.hawb,
            "status": status,
            "riesgos": reasons
        }
    elif role == "forwarder":
        faltantes = [r for r in reasons if "❌" in r]
        return {
            "cargo_id": cargo.id,
            "mawb": cargo.mawb,
            "documentos_faltantes": faltantes,
            "status": status
        }
    elif role == "camionero":
        green_light = "SI" if status == "🟢 LISTA PARA ACEPTACIÓN" else "NO"
        return {
            "cargo_id": cargo.id,
            "mawb": cargo.mawb,
            "puedo_ir": green_light,
            "status": status
        }
    elif role == "warehouse":
        return {
            "cargo_id": cargo.id,
            "mawb": cargo.mawb,
            "status": status,
            "motivos": reasons,
            "accion_recomendada": "ACEPTAR" if status=="🟢 LISTA PARA ACEPTACIÓN" else "HOLD / CORREGIR"
        }
    elif role == "admin":
        return {
            "cargo_id": cargo.id,
            "mawb": cargo.mawb,
            "status": status,
            "motivos": reasons,
            "documentos": [{ "doc_type": d.doc_type, "version": d.version, "responsable": d.responsible } for d in documents]
        }
