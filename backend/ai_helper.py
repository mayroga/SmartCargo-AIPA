# backend/ai_helper.py
"""
Asesor SmartCargo-AIPA
Este módulo NO valida, NO decide, NO bloquea.
Solo explica de forma educativa por qué una regla existe
y cómo corregirla antes de llegar a la aerolínea.
"""

EXPLANATIONS = {
    "InvoiceMissingIncoterm": {
        "en": "The commercial invoice must declare an Incoterm to define responsibility, risk, and cost allocation.",
        "es": "La factura comercial debe declarar un Incoterm para definir responsabilidades, riesgos y costos."
    },
    "PackingListMismatch": {
        "en": "The packing list must match pieces, weight, and volume declared in the invoice and AWB.",
        "es": "El packing list debe coincidir en piezas, peso y volumen con la factura y el AWB."
    },
    "MSDSExpired": {
        "en": "An expired MSDS is not acceptable for air transport.",
        "es": "Una MSDS vencida no es aceptable para transporte aéreo."
    },
    "DGSignatureMissing": {
        "en": "Dangerous Goods documentation must be signed by a certified shipper.",
        "es": "La documentación de mercancías peligrosas debe estar firmada por un shipper certificado."
    }
}

def advisor_explanation(code: str, lang: str = "en") -> str:
    """
    Devuelve una explicación educativa.
    Nunca devuelve estados operativos.
    """
    return EXPLANATIONS.get(code, {}).get(
        lang,
        "Review documentation according to airline and destination requirements."
        if lang == "en"
        else "Revise la documentación según los requisitos de la aerolínea y destino."
    )
