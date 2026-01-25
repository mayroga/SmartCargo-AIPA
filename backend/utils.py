# backend/utils.py

def cargo_dashboard(cargo_data):
    """
    Retorna un semáforo y estado de documentos para el dashboard operativo.
    """
    # Aquí puedes poner reglas duras de Avianca/IATA/DG
    # Ejemplo simplificado:
    semaphore = "🟢"
    if cargo_data.get("cargo_type") == "DG":
        semaphore = "🟡"
    if cargo_data.get("weight", 0) > 1000:
        semaphore = "🔴"
    return {"semaphore": semaphore, "documents": cargo_data.get("documents", [])}

def generate_advisor_message(cargo_data):
    """
    Genera un mensaje educativo explicando el estado del semáforo.
    """
    msg = f"Cargo MAWB {cargo_data.get('mawb')} está en semáforo {cargo_data.get('semaphore')}\n"
    msg += "Explicación educativa: "
    if cargo_data.get("cargo_type") == "DG":
        msg += "Esta carga es DG (Dangerous Goods), debe cumplir reglas especiales de embalaje y documentación.\n"
    if cargo_data.get("weight", 0) > 1000:
        msg += "Peso excede 1000 kg, verificar límites y planes de manejo de carga pesada.\n"
    if not cargo_data.get("documents"):
        msg += "No hay documentos cargados, la carga no puede ser procesada.\n"
    return msg
