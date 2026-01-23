# utils.py
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

DISCLAIMER = (
    "Automated Advisory Report. "
    "This system does not approve, reject, or replace "
    "carrier, operator, or authority decisions."
)

def generate_pdf_report(data, filename):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename)
    story = []

    story.append(Paragraph("<b>Advisory Cargo Document Report</b>", styles["Title"]))
    story.append(Paragraph(f"Date: {datetime.utcnow()}", styles["Normal"]))
    story.append(Paragraph(f"Cargo ID: {data.get('cargo_id')}", styles["Normal"]))
    story.append(Paragraph(f"Status: {data.get('status')}", styles["Normal"]))
    story.append(Paragraph("<br/>Checklist:", styles["Normal"]))

    for k, v in data.get("checklist", {}).items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph(DISCLAIMER, styles["Italic"]))

    doc.build(story)
