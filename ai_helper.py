from typing import List
from models import Documento
import re

def compare_invoice_vs_packing(invoice: Documento, packing: Documento) -> List[str]:
    """
    Detecta incoherencias entre Invoice y Packing List
    """
    errors = []

    # Esto sería un ejemplo: números de piezas
    try:
        invoice_pcs = int(re.search(r"\b\d+\b", invoice.comment or "0").group())
        packing_pcs = int(re.search(r"\b\d+\b", packing.comment or "0").group())
        if invoice_pcs != packing_pcs:
            errors.append(f"Piezas no coinciden: Invoice {invoice_pcs} vs Packing {packing_pcs}")
    except:
        pass
    return errors

def validate_pdf_format(doc: Documento) -> bool:
    """
    Detecta si el PDF cumple formato esperado
    """
    # Ejemplo básico: solo verificar extensión
    return doc.name.lower().endswith(('.pdf', '.docx'))

def ai_document_checker(documents: List[Documento]) -> List[Documento]:
    """
    IA auxiliar: valida coherencia y formatos, solo para soporte
    """
    for doc in documents:
        # Validación simple de formato
        if not validate_pdf_format(doc):
            doc.status = "⚠ Dudoso"
            doc.comment = "Formato de archivo inválido"

    # Comparar invoice vs packing list si ambos existen
    invoice = next((d for d in documents if d.name == "invoice"), None)
    packing = next((d for d in documents if d.name == "packingList"), None)
    if invoice and packing:
        errors = compare_invoice_vs_packing(invoice, packing)
        if errors:
            invoice.status = "⚠ Dudoso"
            invoice.comment = "; ".join(errors)
    return documents
