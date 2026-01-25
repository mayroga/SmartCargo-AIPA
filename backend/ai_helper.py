# backend/ai_helper.py
# Asesor SmartCargo-AIPA (NO valida, SOLO explica)

def advisor_explanation(semaphore: str, motivos: list) -> str:
    if semaphore.startswith("🟢"):
        return (
            "La carga cumple con los documentos mínimos requeridos. "
            "No se detectan riesgos operativos inmediatos para presentación en counter."
        )

    if semaphore.startswith("🟡"):
        return (
            "La carga puede presentarse, pero existen observaciones que "
            "podrían generar hold o reproceso en counter si no se corrigen."
        )

    return (
        "La carga NO debe enviarse. "
        "Existen incumplimientos documentales u operativos que impedirán su aceptación."
    )
