# rules.py – Validación de Carga SmartCargo-AIPA

from datetime import datetime

REQUIRED_DOCS = [
    "Commercial Invoice",
    "Packing List",
    "SLI",
    "MSDS",
    "Certificado de origen",
    "Certificado fitosanitario",
    "Licencia materiales peligrosos",
    "Bill of Lading / Air Waybill",
    "Seguro / Aduana",
    "Harmonized Code"
]

def validate_cargo(cargo: dict) -> dict:
    """
    Valida un cargo según documentos obligatorios, peso, volumen y consistencia.
    Retorna:
    {
        "cargo_id": str,
        "weight": float,
        "volume": float,
        "semaphore": "OK"|"REVISAR"|"BLOQUEADO",
        "documents": [{"doc_type":..., "status":..., "observation":..., "norm":...}],
        "legal": str,
        "motivos": list
    }
    """
    cargo_id = cargo.get("mawb", "N/A")
    weight = float(cargo.get("weight", 0))
    volume = float(cargo.get("volume", 0))
    flight_date = cargo.get("flight_date", "")
    doc_list = cargo.get("documents", [])

    docs_status = []
    motivos = []
    semaforo = "OK"
    legal_alerts = []

    # Revisar documentos obligatorios
    for req in REQUIRED_DOCS:
        doc = next((d for d in doc_list if d.get("doc_type") == req), None)
        if not doc:
            docs_status.append({
                "doc_type": req,
                "status": "Crítico",
                "observation": "Documento faltante",
                "norm": "IATA / Avianca"
            })
            motivos.append(f"Falta {req}")
            semaforo = "BLOQUEADO"
            legal_alerts.append(f"{req} requerido por normas IATA")
        else:
            # Validación simple de contenido y expiración
            status = "Aprobado"
            observation = doc.get("observation") or ""
            norm = doc.get("norm") or "IATA"

            if doc.get("expired", False):
                status = "Crítico"
                observation += " (Documento vencido)"
                semaforo = "BLOQUEADO"
                motivos.append(f"{req} vencido")
                legal_alerts.append(f"{req} vencido")

            elif observation:
                status = "Observación"
                if semaforo != "BLOQUEADO":
                    semaforo = "REVISAR"
                motivos.append(f"{req} observación")
                legal_alerts.append(f"{req}: {observation}")

            docs_status.append({
                "doc_type": req,
                "status": status,
                "observation": observation or "—",
                "norm": norm
            })

    # Validación de peso y volumen (ejemplo)
    max_weight = 5000  # kg
    max_volume = 50  # m³
    if weight > max_weight:
        semaforo = "BLOQUEADO"
        motivos.append(f"Peso {weight} kg excede límite {max_weight} kg")
        legal_alerts.append("Límite de peso excedido por Avianca")

    if volume > max_volume:
        if semaforo != "BLOQUEADO":
            semaforo = "REVISAR"
        motivos.append(f"Volumen {volume} m³ excede límite {max_volume} m³")
        legal_alerts.append("Volumen excede límite")

    return {
        "cargo_id": cargo_id,
        "weight": weight,
        "volume": volume,
        "semaphore": semaforo,
        "documents": docs_status,
        "legal": "; ".join(legal_alerts) if legal_alerts else "Sin alertas",
        "motivos": motivos
    }
