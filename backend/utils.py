# utils.py
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

DISCLAIMER = (
    "Automated Advisory Report. "
    "This system does not approve, reject, or replace "
    "carrier, operator, or authority decisions."
)

def validate_documents(cargo_type, uploaded_docs, rules):
    result = {
        "status": "READY",
        "missing": [],
        "warnings": [],
        "checklist": {}
    }

    required = rules[cargo_type]["required"]

    for doc in required:
        if doc in uploaded_docs:
            result["checklist"][doc] = "OK"
        else:
            result["checklist"][doc] = "MISSING"
            result["missing"].append(doc)

    if result["missing"]:
        result["status"] = "HOLD"

    return result

def generate_pdf_report(data, filename):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename)
    story = []

    story.append(Paragraph("<b>Advisory Cargo Document Report</b>", styles["Title"]))
    story.append(Paragraph(f"Date: {datetime.utcnow()}", styles["Normal"]))
    story.append(Paragraph(f"AWB: {data['awb']}", styles["Normal"]))
    story.append(Paragraph(f"Cargo Type: {data['cargo_type']}", styles["Normal"]))
    story.append(Paragraph(f"Status: <b>{data['status']}</b>", styles["Normal"]))
    story.append(Paragraph("<br/>Checklist:", styles["Normal"]))

    for k, v in data["checklist"].items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph(DISCLAIMER, styles["Italic"]))

    doc.build(story)
