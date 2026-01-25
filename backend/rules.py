from datetime import datetime

REQUIRED_DOCS = {
    "GEN": [
        "Commercial Invoice",
        "Packing List",
        "SLI",
        "Bill of Lading / Air Waybill",
        "Harmonized Code"
    ],
    "DG": [
        "MSDS",
        "DGD",
        "Commercial Invoice",
        "Packing List",
        "SLI",
        "Bill of Lading / Air Waybill"
    ],
    "PER": [
        "Health Certificate",
        "Commercial Invoice",
        "Packing List",
        "Bill of Lading / Air Waybill"
    ]
}

MAX_WEIGHT_KG = 5000
MAX_VOLUME_M3 = 50
MAX_DIM_CM = 300  # máximo largo/ancho/alto

def validate_cargo(cargo: dict) -> dict:
    cargo_id = cargo.get("mawb", "N/A")
    cargo_type = cargo.get("cargo_type", "GEN").upper()
    weight = float(cargo.get("weight", 0))
    volume = float(cargo.get("volume", 0))
    length = float(cargo.get("length", 0))
    width = float(cargo.get("width", 0))
    height = float(cargo.get("height", 0))
    flight_date = cargo.get("flight_date", "")
    doc_list = cargo.get("documents", [])

    semaforo = "🟢"
    motivos = []
    docs_status = []

    # Validación de documentos obligatorios
    required = REQUIRED_DOCS.get(cargo_type, [])
    present_docs = [d["doc_type"] for d in doc_list]
    for req in required:
        doc = next((d for d in doc_list if d["doc_type"] == req), None)
        if not doc:
            docs_status.append({"doc_type": req, "status": "🔴", "observation": "Documento faltante"})
            motivos.append(f"Falta {req}")
            semaforo = "🔴"
        else:
            status = "🟢"
            obs = ""
            if doc.get("expired", False):
                status = "🔴"
                obs = "Documento vencido"
                semaforo = "🔴"
                motivos.append(f"{req} vencido")
            docs_status.append({"doc_type": req, "status": status, "observation": obs})

    # Validación peso/volumen/dimensiones
    if weight > MAX_WEIGHT_KG:
        semaforo = "🔴"
        motivos.append(f"Peso {weight}kg excede {MAX_WEIGHT_KG}kg")
    if volume > MAX_VOLUME_M3:
        semaforo = "🟡" if semaforo != "🔴" else semaforo
        motivos.append(f"Volumen {volume}m³ excede {MAX_VOLUME_M3}m³")
    for dim, val in zip(["largo","ancho","alto"], [length, width, height]):
        if val > MAX_DIM_CM:
            semaforo = "🔴"
            motivos.append(f"{dim} {val}cm excede {MAX_DIM_CM}cm")

    return {
        "cargo_id": cargo_id,
        "weight": weight,
        "volume": volume,
        "length": length,
        "width": width,
        "height": height,
        "semaphore": semaforo,
        "documents": docs_status,
        "motivos": motivos
    }
