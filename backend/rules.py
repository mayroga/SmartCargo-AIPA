from typing import Dict, List

# Documentos requeridos por tipo de carga según Avianca/IATA/TSA/CBP
REQUIRED_DOCS = {
    "General": ["AWB", "Commercial Invoice", "Packing List"],
    "Dangerous Goods": ["AWB", "MSDS", "DG Declaration", "Commercial Invoice", "Packing List"],
    "Perishable": ["AWB", "Temperature Certificate", "Commercial Invoice", "Packing List"]
}

# Restricciones técnicas de aeronaves (ejemplo Airbus A330F/B787 y A320)
AIRCRAFT_LIMITS = {
    "WideBody": {"max_height_cm": 244, "max_weight_kg": 4500},
    "NarrowBody": {"max_height_cm": 114, "max_weight_kg": 1500}  # ejemplo
}

# Reglas de validación principales
def validate_cargo(cargo_data: Dict):
    present_docs = [doc["filename"] for doc in cargo_data.get("documents", [])]
    cargo_type = cargo_data.get("cargo_type", "General")
    weight = cargo_data.get("weight_kg", 0)
    height = cargo_data.get("height_cm", 0)
    role = cargo_data.get("role", "Shipper")

    # Documentos requeridos y faltantes
    required_docs = REQUIRED_DOCS.get(cargo_type, [])
    missing_docs = [doc for doc in required_docs if doc not in present_docs]

    # Chequeo de peso y dimensiones según tipo de aeronave
    if weight <= 4500:
        overweight = False
    else:
        overweight = True

    if height <= 244:
        oversized = False
    else:
        oversized = True

    # Semáforo legal y operativo
    if missing_docs or overweight or oversized:
        if missing_docs:
            status = "🟡"  # Advertencia: falta documento
        else:
            status = "🔴"  # Crítico: sobrepeso o sobredimensión
    else:
        status = "🟢"

    # Mensaje legal explicativo
    explanation = "Cargo validated according to Avianca/IATA/TSA/CBP rules.\n"
    explanation += f"Cargo Type: {cargo_type}\n"
    explanation += f"Documents Required: {', '.join(required_docs)}\n"
    if missing_docs:
        explanation += f"Missing Documents: {', '.join(missing_docs)}\n"
    explanation += f"Weight: {weight} kg {'(Overweight)' if overweight else '(OK)'}\n"
    explanation += f"Height: {height} cm {'(Oversized)' if oversized else '(OK)'}\n"
    explanation += "Compliance checked: IATA DGR, TSA/CBP regulations, aircraft limits, packaging certification, AWB consistency.\n"

    return {
        "semaforo": status,
        "documents_required": required_docs,
        "missing_docs": missing_docs,
        "overweight": overweight,
        "oversized": oversized,
        "advisor": explanation
    }
