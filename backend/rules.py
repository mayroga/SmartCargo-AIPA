from typing import Dict

# Documentos requeridos por tipo de carga según Avianca/IATA/TSA/CBP
REQUIRED_DOCS = {
    "General": ["AWB", "Commercial Invoice", "Packing List"],
    "Dangerous Goods": ["AWB", "MSDS", "DG Declaration", "Commercial Invoice", "Packing List"],
    "Perishable": ["AWB", "Temperature Certificate", "Commercial Invoice", "Packing List"]
}

# Semáforo según estado de documentos y reglas
def calculate_semaforo(cargo_data: Dict, present_docs: list):
    required = REQUIRED_DOCS.get(cargo_data["cargo_type"], [])
    missing = [doc for doc in required if doc not in present_docs]

    # Reglas de pesos y dimensiones máximas (ejemplo Avianca)
    weight_kg = cargo_data["weight_kg"]
    length_cm = cargo_data["length_cm"]
    width_cm = cargo_data["width_cm"]
    height_cm = cargo_data["height_cm"]

    max_weight_kg = 1000
    max_dimension_cm = 300  # en cada eje
    overweight = weight_kg > max_weight_kg
    oversized = any(dim > max_dimension_cm for dim in [length_cm, width_cm, height_cm])

    if missing or overweight or oversized:
        status = "🟡" if missing else "🔴"
    else:
        status = "🟢"

    return status, missing, overweight, oversized

# Validación de cargo estricta
def validate_cargo(cargo_data: Dict):
    # Aquí se simula que el sistema verifica las reglas sin usar IA para validar documentos
    present_docs = cargo_data.get("documents", [])
    semaforo, missing, overweight, oversized = calculate_semaforo(cargo_data, present_docs)

    return {
        "semaforo": semaforo,
        "missing_docs": missing,
        "overweight": overweight,
        "oversized": oversized,
        "required_docs": REQUIRED_DOCS.get(cargo_data["cargo_type"], [])
    }
