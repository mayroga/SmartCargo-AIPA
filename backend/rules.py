from datetime import datetime

# Reglas Avianca-first
def validate_cargo(cargo, documents):
    """
    Retorna:
    status: 🔴 NO ACEPTABLE / 🟡 ACEPTABLE CON RIESGO / 🟢 LISTA PARA ACEPTACIÓN
    reasons: lista de motivos
    """
    reasons = []
    status = "🟢 LISTA PARA ACEPTACIÓN"

    # Regla 1: Documentos obligatorios por tipo de carga
    mandatory_docs = ["Invoice", "PackingList", "SLI"]
    if cargo.cargo_type == "DG":
        mandatory_docs.append("MSDS")
    if cargo.cargo_type == "HUM":
        mandatory_docs.append("PermisoSanitario")
    if cargo.cargo_type == "VAL":
        mandatory_docs.append("Insurance")

    doc_types = [d.doc_type for d in documents]

    for md in mandatory_docs:
        if md not in doc_types:
            reasons.append(f"❌ Falta {md}")
            status = "🔴 NO ACEPTABLE"

    # Regla 2: Revisar versiones y fechas
    for d in documents:
        if d.doc_type in ["MSDS"] and d.version and d.version < datetime.now().strftime("%Y-%m-%d"):
            reasons.append(f"❌ {d.doc_type} vencido")
            status = "🔴 NO ACEPTABLE"

    return status, reasons
