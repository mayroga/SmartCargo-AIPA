# src/logic/reporting.py
import os
import json
from config.env_keys import BASE_URL

def generate_pdf_logic(shipment, rtc_payload=None, is_advanced=False):
    """
    Placeholder para la generación de PDF. En esta versión devuelve
    una URL esperada donde el PDF estará disponible.
    - Recomiendo reemplazar este stub por la generación real de PDF (reportlab / wkhtmltopdf).
    - Crea un JSON resumen en static/reports/ para auditoría (opcional).
    """
    reports_dir = os.path.join('static', 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    filename_base = f"rtc_{shipment.shipment_id}"
    json_path = os.path.join(reports_dir, f"{filename_base}.json")

    summary = {
        "shipment_id": str(shipment.shipment_id),
        "is_advanced": bool(is_advanced),
        "rtc_payload": rtc_payload or {},
    }

    # Guardar resumen (auditable) - el PDF real puede generarse fuera o por otro proceso
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # URL que el frontend puede usar para descargar (tu servidor debe servir /static/reports)
    pdf_filename = f"{filename_base}.pdf"
    pdf_url = f"{BASE_URL.rstrip('/')}/static/reports/{pdf_filename}"
    return pdf_url
