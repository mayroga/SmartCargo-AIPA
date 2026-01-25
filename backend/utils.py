from backend.rules import validate_cargo_rules

# Genera dashboard operativo
def cargo_dashboard(cargo_data, validation_status):
    return {
        "semaforo": validation_status["semaforo"],
        "documents_required": validation_status["required_docs"]
    }

# Genera asesor educativo explicando semáforo
def generate_advisor_message(cargo_data, validation_status):
    msg = []
    if validation_status["semaforo"] == "🟢":
        msg.append("All checks passed. Cargo ready for shipment.")
    if validation_status["missing_docs"]:
        msg.append(f"Missing documents: {', '.join(validation_status['missing_docs'])}. Upload immediately.")
    if validation_status["overweight"]:
        msg.append("Cargo exceeds maximum weight. Check with airline.")
    if validation_status["oversized"]:
        msg.append("Cargo dimensions exceed allowed limits. Review packaging.")
    return " | ".join(msg)
