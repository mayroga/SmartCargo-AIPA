# backend/rules.py
from datetime import datetime, timedelta

# Documentos obligatorios SmartCargo-AIPA
MANDATORY_DOCS = [
    "Commercial Invoice",
    "Packing List",
    "SLI",
    "MSDS",
    "Certificado de origen",
    "Certificado de fumigación",
    "Licencia transporte materiales peligrosos",
    "Bill of Lading / MAWB / HAWB",
    "Documentos de seguros",
    "Documentos de aduanas",
    "Harmonized codes y descripción de mercancía"
]

def validate_cargo_documents(cargo):
    """
    Validación avanzada de cargo para Avianca/IATA/CBP/TSA/DOT.
    Devuelve:
    - semaforo: 🟢, 🟡, 🔴
    - motivos: lista de alertas y documentos faltantes
    - detalles: diccionario completo de revisión de documentos
    """
    motivos = []
    detalles = {}
    semaforo = "🟢 LISTO"

    # Diccionario de documentos existentes
    existing_docs = {doc.doc_type: doc for doc in cargo.documents}

    # Validación de documentos obligatorios
    for doc_name in MANDATORY_DOCS:
        if doc_name not in existing_docs:
            motivos.append(f"Falta {doc_name}")
            detalles[doc_name] = "❌ Faltante"
        else:
            doc = existing_docs[doc_name]
            # Revisar vencimiento si aplica
            if hasattr(doc, "expiration_date") and doc.expiration_date:
                if doc.expiration_date < datetime.today():
                    motivos.append(f"{doc_name} vencido")
                    detalles[doc_name] = "⚠️ Vencido"
                else:
                    detalles[doc_name] = "✅ Vigente"
            else:
                detalles[doc_name] = "✅ Cargado"

    # Validación de peso y volumen
    if cargo.weight > 1000:
        motivos.append(f"Peso {cargo.weight} kg excede límite de Avianca")
    if cargo.volume > 10:
        motivos.append(f"Volumen {cargo.volume} m³ excede límite permitido")

    # Consistencia entre documentos clave
    ci = existing_docs.get("Commercial Invoice")
    pl = existing_docs.get("Packing List")
    if ci and pl:
        if getattr(ci, "filename", "") != getattr(pl, "filename", ""):
            motivos.append("Packing List no coincide con Invoice")

    # Tipo de mercancía y alertas legales
    if getattr(cargo, "cargo_type", "").lower() in ["peligrosa", "dangerous"]:
        motivos.append("Carga peligrosa requiere manejo especial")

    # Determinar semáforo
    if motivos:
        semaforo = "🔴 NO ACEPTABLE"
    else:
        semaforo = "🟢 LISTO"

    return semaforo, motivos, detalles
