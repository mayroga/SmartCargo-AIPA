# backend/rules.py
from datetime import datetime

LEGAL_DISCLAIMER = (
    "SMARTCARGO-AIPA by May Roga LLC | "
    "Preventive documentary validation system. "
    "Does not replace airline operational decisions. "
    "Generated evidence is for operational and educational purposes only."
)

REQUIRED_DOCS_BY_TYPE = {
    "GEN": ["Commercial Invoice", "Packing List", "AWB"],
    "DG": ["Commercial Invoice", "Packing List", "AWB", "MSDS", "DGD"],
    "PER": ["Commercial Invoice", "Packing List", "AWB", "Health Certificate"],
    "HUM": ["Commercial Invoice", "Packing List", "AWB", "Export Permit"],
    "VAL": ["Commercial Invoice", "Packing List", "AWB", "Insurance"]
}

def validate_cargo(cargo: dict) -> dict:
    """
    REGLAS DURAS.
    Sin IA.
    Sin criterio humano.
    """
    docs = cargo.get("documents", [])
    cargo_type = cargo.get("cargo_type")
    weight = cargo.get("weight", 0)
    volume = cargo.get("volume", 0)

    motivos = []
    documents_result = []
    semaphore = "🟢 LISTA PARA ACEPTACIÓN"

    required_docs = REQUIRED_DOCS_BY_TYPE.get(cargo_type, [])

    for req in required_docs:
        found = next((d for d in docs if d["doc_type"] == req), None)
        if not found:
            documents_result.append({
                "doc_type": req,
                "status": "❌ NO ACEPTABLE",
                "reason_code": "MissingDocument"
            })
            motivos.append(f"Missing {req}")
            semaphore = "🔴 NO ACEPTABLE"
        else:
            documents_result.append({
                "doc_type": req,
                "status": "✔ OK",
                "reason_code": None
            })

    if weight > 5000:
        semaphore = "🔴 NO ACEPTABLE"
        motivos.append("Weight exceeds aircraft limitation")

    if volume > 50 and semaphore != "🔴 NO ACEPTABLE":
        semaphore = "🟡 ACEPTABLE CON RIESGO"
        motivos.append("Volume close to operational limit")

    return {
        "mawb": cargo.get("mawb"),
        "semaphore": semaphore,
        "documents": documents_result,
        "motivos": motivos,
        "legal": LEGAL_DISCLAIMER
    }
