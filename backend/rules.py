# backend/rules.py
from datetime import datetime

def validate_cargo_documents(cargo):
    """
    Aplica el checklist de Avianca, IATA, CBP, TSA, DOT.
    Devuelve:
      semáforo: 🔴 NO ACEPTABLE / 🟡 ACEPTABLE CON RIESGO / 🟢 LISTO PARA COUNTER
      motivos: lista de razones claras
    """

    motivos = []
    semaforo = "🟢 LISTO PARA COUNTER"

    # Convertir documentos en diccionario para fácil acceso
    docs = {doc.doc_type: doc for doc in cargo.documents}

    # Documentos obligatorios
    required_docs = ["Commercial Invoice", "Packing List", "SLI", "MSDS"]

    for doc_name in required_docs:
        if doc_name not in docs:
            motivos.append(f"Falta {doc_name}")
    
    # Packing List vs Invoice (consistencia mínima)
    if "Commercial Invoice" in docs and "Packing List" in docs:
        invoice = docs["Commercial Invoice"]
        packing = docs["Packing List"]
        if invoice.filename != packing.filename:
            motivos.append("Packing List no coincide con Invoice")

    # MSDS vigente
    if "MSDS" in docs:
        msds = docs["MSDS"]
        if hasattr(msds, "expiration_date") and msds.expiration_date:
            if msds.expiration_date < datetime.today():
                motivos.append("MSDS vencido")

    # Determinar semáforo según gravedad
    if motivos:
        semaforo = "🔴 NO ACEPTABLE"
    else:
        semaforo = "🟢 LISTO PARA COUNTER"

    # Nota legal incluida siempre
    motivos.append("SmartCargo-AIPA es asesor, no autoridad. La aceptación final depende de Avianca, IATA, CBP, TSA y DOT.")

    return semaforo, motivos
