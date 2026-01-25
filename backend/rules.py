# backend/rules.py
# SMARTCARGO-AIPA by May Roga LLC
# Motor de validación documental PREVENTIVO (NO IA)

from datetime import datetime

# -------------------------------
# Checklists Avianca-first
# -------------------------------

BASE_REQUIRED_DOCS = [
    "Commercial Invoice",
    "Packing List",
    "Air Waybill",
]

DG_REQUIRED_DOCS = BASE_REQUIRED_DOCS + [
    "Shipper Declaration DGR",
    "MSDS",
]

PER_REQUIRED_DOCS = BASE_REQUIRED_DOCS + [
    "Health Certificate",
    "Temperature Statement",
]

# -------------------------------
# Validación principal
# -------------------------------

def validate_cargo(cargo: dict) -> dict:
    """
    Retorna SIEMPRE un resultado operativo.
    NO guarda nada.
    NO usa IA.
    """

    motivos = []
    documents_status = []
    semaphore = "🟢 LISTA PARA ACEPTACIÓN"

    cargo_type = cargo.get("cargo_type", "GEN")
    docs = cargo.get("documents", [])

    if cargo_type == "DG":
        required_docs = DG_REQUIRED_DOCS
    elif cargo_type == "PER":
        required_docs = PER_REQUIRED_DOCS
    else:
        required_docs = BASE_REQUIRED_DOCS

    # -------------------------------
    # Validar documentos obligatorios
    # -------------------------------
    for req in required_docs:
        found = next((d for d in docs if d["doc_type"] == req), None)

        if not found:
            documents_status.append({
                "doc_type": req,
                "status": "❌ NO PRESENTE",
                "observation": "Documento obligatorio faltante",
                "norm": "Avianca / IATA"
            })
            motivos.append(f"Falta {req}")
            semaphore = "🔴 NO ACEPTABLE"
        else:
            documents_status.append({
                "doc_type": req,
                "status": "✔ PRESENTE",
                "observation": "—",
                "norm": "Avianca / IATA"
            })

    # -------------------------------
    # Validaciones duras adicionales
    # -------------------------------
    weight = float(cargo.get("weight", 0))
    volume = float(cargo.get("volume", 0))

    if weight <= 0 or volume <= 0:
        semaphore = "🔴 NO ACEPTABLE"
        motivos.append("Peso o volumen inválido")

    if weight > 5000:
        semaphore = "🔴 NO ACEPTABLE"
        motivos.append("Peso excede límites operativos")

    if semaphore != "🔴 NO ACEPTABLE" and motivos:
        semaphore = "🟡 ACEPTABLE CON RIESGO"

    # -------------------------------
    # Blindaje legal SIEMPRE visible
    # -------------------------------
    legal = (
        "SMARTCARGO-AIPA by May Roga LLC · "
        "Sistema de validación documental preventiva. "
        "No sustituye decisiones del operador aéreo. "
        "Resultado generado para fines operativos y educativos."
    )

    return {
        "semaphore": semaphore,
        "documents": documents_status,
        "motivos": motivos,
        "legal": legal
    }
