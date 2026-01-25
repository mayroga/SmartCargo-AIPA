# ai_helper.py
def ai_document_hint(doc_type: str, cargo_type: str) -> str:
    """
    Sugerencias automáticas para documentos según tipo de carga.
    Placeholder IA – no genera texto operativo, solo ayuda a detectar errores.
    """
    hints = {
        "DG": {
            "MSDS": "Verificar que incluya UN number, clase de riesgo y firma.",
            "DGD": "Debe cumplir IATA DGR y estar firmada."
        },
        "PER": {
            "HealthCert": "Debe indicar temperatura y origen aprobado."
        },
        "GEN": {
            "Invoice": "Revisar consistencia MAWB / HAWB."
        }
    }

    return hints.get(cargo_type, {}).get(doc_type, "Documento recibido. Validación manual requerida.")
