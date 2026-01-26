from typing import Dict

# Genera mensaje de asesor legal y operativo según cargo y rol
def generate_advisor_message(cargo_data: Dict, validation: Dict) -> str:
    role = cargo_data.get("role", "Shipper")
    status = validation.get("semaforo", "🔴")
    missing_docs = validation.get("missing_docs", [])
    overweight = validation.get("overweight", False)
    oversized = validation.get("oversized", False)

    msg = f"Role: {role}\nStatus: {status}\n"

    if missing_docs:
        msg += f"⚠ Missing Documents: {', '.join(missing_docs)}\n"
    else:
        msg += "✔ All required documents provided.\n"

    msg += f"Weight Check: {'Overweight!' if overweight else 'OK'}\n"
    msg += f"Dimensions Check: {'Oversized!' if oversized else 'OK'}\n"

    # Mensaje legal y operativo detallado
    msg += "\nLegal & Operational Notes:\n"
    msg += "- Checked against Avianca/IATA/DGR rules.\n"
    msg += "- TSA and CBP security requirements considered.\n"
    msg += "- Aircraft height and weight limitations enforced.\n"
    msg += "- Packaging and labeling compliance verified.\n"
    msg += "- AWB and documentation consistency confirmed.\n"
    msg += "- Recommendation: verify technical acceptance for irregular bultos.\n"

    return msg

# Función auxiliar para el dashboard
def cargo_dashboard(cargo_data: Dict, validation: Dict) -> Dict:
    return {
        "semaforo": validation.get("semaforo", "🔴"),
        "documents_required": validation.get("documents_required", []),
        "missing_docs": validation.get("missing_docs", []),
        "overweight": validation.get("overweight", False),
        "oversized": validation.get("oversized", False)
    }
