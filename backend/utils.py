from typing import Dict

# ------------------------
# Dashboard y asesor
# ------------------------

def cargo_dashboard(cargo_data: Dict) -> Dict:
    """
    Genera semáforo operativo para cargo según reglas.
    """
    semaforo = "🟢"
    reasons = []

    # Peso máximo por tipo de cargo
    if cargo_data["weight"] > 1000:
        semaforo = "🟡"
        reasons.append(f"Peso {cargo_data['weight']}kg excede límite recomendado para transporte aéreo estándar")

    # Volumen máximo por tipo de carga
    if cargo_data["volume"] > 5:
        semaforo = "🟡"
        reasons.append(f"Volumen {cargo_data['volume']}m³ supera lo recomendable")

    # Check básico de origen y destino
    if not cargo_data["origin"] or not cargo_data["destination"]:
        semaforo = "🔴"
        reasons.append("Origen o destino no definido")

    # Check de documentos esenciales
    if cargo_data.get("role") in ["Shipper", "Forwarder"]:
        # Ejemplo: el sistema podría exigir ciertos documentos
        required_docs = ["Commercial Invoice", "Packing List", "AWB"]
        uploaded_docs = cargo_data.get("uploaded_files", [])
        missing = [doc for doc in required_docs if doc not in uploaded_docs]
        if missing:
            semaforo = "🟡"
            reasons.append(f"Documentos faltantes: {', '.join(missing)}")

    return {"semaforo": semaforo, "reasons": reasons}

def generate_advisor_message(cargo_data: Dict, cargo_status: Dict) -> str:
    """
    Genera un mensaje educativo explicando semáforo y decisiones.
    """
    role = cargo_data.get("role", "Usuario")
    semaforo = cargo_status.get("semaforo", "🟢")
    reasons = cargo_status.get("reasons", [])

    msg = f"SMARTCARGO-AIPA by May Roga LLC · Sistema de validación documental preventiva.\n"
    msg += f"Rol: {role}\n"
    msg += f"Semáforo operativo: {semaforo}\n"
    if reasons:
        msg += "Motivos:\n"
        for r in reasons:
            msg += f"- {r}\n"
    else:
        msg += "- Todo en orden según reglas Avianca/IATA/DG/PER.\n"
    msg += "Este sistema actúa como muro preventivo educativo. No sustituye decisiones del operador aéreo."
    return msg
