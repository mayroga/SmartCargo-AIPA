# backend/rules.py

from typing import List, Dict
from storage import list_documents
from datetime import datetime

# Checklists Avianca por tipo de carga
CHECKLISTS = {
    "GEN": ["Commercial Invoice", "Packing List", "AWB"],
    "DG": ["Commercial Invoice", "Packing List", "AWB", "Shipper's Letter of Instruction", "MSDS", "Certificado"],
    "PER": ["Commercial Invoice", "Packing List", "AWB", "Permiso País Destino"],
    "HUM": ["Commercial Invoice", "Packing List", "AWB", "Certificado"],
    "AVI": ["Commercial Invoice", "Packing List", "AWB", "Permiso País Destino"],
    "VAL": ["Commercial Invoice", "Packing List", "AWB", "Certificado"]
}

# Reglas especiales por país de destino
PAIS_REGLAS = {
    "Cuba": ["Permiso País Destino", "Certificado"],
    "USA": ["Certificado"]
}

# Semáforo operativo
def evaluate_semaforo(missing_docs: List[str], warnings: List[str]) -> str:
    if missing_docs:
        return "🔴 NO ACEPTABLE"
    elif warnings:
        return "🟡 ACEPTABLE CON RIESGO"
    else:
        return "🟢 ACEPTABLE"

def get_required_documents(tipo_carga: str, pais_destino: str) -> List[str]:
    """
    Devuelve lista de documentos obligatorios según tipo de carga y país de destino
    """
    required = CHECKLISTS.get(tipo_carga, [])
    country_rules = PAIS_REGLAS.get(pais_destino, [])
    combined = list(set(required + country_rules))
    return combined

def validate_cargo(cargo_id: str, tipo_carga: str, pais_destino: str) -> Dict:
    """
    Valida un cargo completo:
    - Verifica documentos obligatorios
    - Genera semáforo operativo
    - Retorna detalle de faltantes, advertencias y semáforo
    """
    required_docs = get_required_documents(tipo_carga, pais_destino)
    uploaded_docs = list_documents(cargo_id)
    uploaded_doc_names = [f.split("_")[0] for f in uploaded_docs]

    missing_docs = [doc for doc in required_docs if doc not in uploaded_doc_names]
    warnings = []

    # Ejemplo de advertencia: MSDS cerca de vencimiento
    for doc_file in uploaded_docs:
        if "MSDS" in doc_file:
            try:
                version = doc_file.split("_")[1]  # timestamp como version
                doc_date = datetime.strptime(version, "%Y%m%d%H%M%S")
                delta = (datetime.now() - doc_date).days
                if delta > 365:
                    warnings.append(f"MSDS vencido o muy antiguo ({delta} días)")
            except:
                warnings.append("MSDS formato de versión inválido")

    semaforo = evaluate_semaforo(missing_docs, warnings)

    return {
        "cargo_id": cargo_id,
        "tipo_carga": tipo_carga,
        "pais_destino": pais_destino,
        "uploaded_docs": uploaded_docs,
        "missing_docs": missing_docs,
        "warnings": warnings,
        "semaforo": semaforo
    }

