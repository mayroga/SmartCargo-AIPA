# main.py

from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import tempfile
import os

# PDF
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Backend imports
from backend.models import Base, engine, SessionLocal, Cargo, Document
from backend.rules import validate_cargo, advisory_result

# Storage functions
from storage import save_document, list_documents, get_document_path, delete_document, validate_documents

# -------------------- APP --------------------
app = FastAPI(title="SmartCargo-AIPA")

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Montar carpeta estática
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------- HOME --------------------
@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>index.html not found</h1>"

# -------------------- CARGO --------------------
@app.post("/cargo/create")
def create_cargo(
    mawb: str = Form(...),
    hawb: str = Form(None),
    airline: str = Form("Avianca Cargo"),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...),
    created_by: str = Form("system")
):
    db = SessionLocal()

    cargo = Cargo(
        mawb=mawb,
        hawb=hawb,
        airline=airline,
        origin=origin,
        destination=destination,
        cargo_type=cargo_type,
        flight_date=datetime.fromisoformat(flight_date),
        created_by=created_by
    )

    db.add(cargo)
    db.commit()
    db.refresh(cargo)
    db.close()

    return {"cargo_id": cargo.id}

@app.get("/cargo/list")
def list_cargos():
    db = SessionLocal()
    cargos = db.query(Cargo).all()
    result = []

    for c in cargos:
        docs = db.query(Document).filter(Document.cargo_id == c.id).all()
        result.append({
            "cargo_id": c.id,
            "mawb": c.mawb,
            "hawb": c.hawb,
            "airline": c.airline,
            "origin": c.origin,
            "destination": c.destination,
            "cargo_type": c.cargo_type,
            "flight_date": c.flight_date.isoformat(),
            "documents": [
                {
                    "doc_type": d.doc_type,
                    "filename": d.filename,
                    "version": d.version,
                    "status": d.status,
                    "responsible": d.responsible,
                    "upload_date": d.upload_date.isoformat()
                } for d in docs
            ]
        })

    db.close()
    return result

# -------------------- UPLOAD DOCUMENT --------------------
@app.post("/cargo/{cargo_id}/upload")
def upload_document(
    cargo_id: int,
    doc_type: str = Form(...),
    responsible: str = Form(...),
    file: UploadFile = File(...)
):
    db = SessionLocal()

    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        db.close()
        raise HTTPException(status_code=404, detail="Cargo not found")

    doc = save_document(db, file, cargo_id, doc_type, responsible)
    db.close()

    return {"status": "uploaded", "version": doc.version}

# -------------------- PDF ADVISORY --------------------
@app.get("/cargo/report/pdf/{cargo_id}")
def advisory_pdf(cargo_id: int):
    db = SessionLocal()

    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        db.close()
        raise HTTPException(status_code=404, detail="Cargo not found")

    docs = db.query(Document).filter(Document.cargo_id == cargo_id).all()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf = SimpleDocTemplate(tmp.name, pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    elements.append(Paragraph("<b>SmartCargo-AIPA by May Roga LLC</b>", styles["Title"]))
    elements.append(Paragraph("Cargo Documentation Advisory Report<br/><br/>", styles["Normal"]))

    # Datos del cargo
    elements.append(Paragraph(f"<b>MAWB:</b> {cargo.mawb}", styles["Normal"]))
    elements.append(Paragraph(f"<b>HAWB:</b> {cargo.hawb or '-'}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Airline:</b> {cargo.airline}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Origin:</b> {cargo.origin}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Destination:</b> {cargo.destination}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Cargo Type:</b> {cargo.cargo_type}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Flight Date:</b> {cargo.flight_date.strftime('%Y-%m-%d')}", styles["Normal"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # Tabla de documentos
    table_data = [["Document", "Version", "Status", "Responsible", "Audit Notes"]]
    for d in docs:
        table_data.append([
            d.doc_type,
            d.version,
            d.status,
            d.responsible,
            d.audit_notes or ""
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (1,1), (-1,-1), "CENTER")
    ]))
    elements.append(table)
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # Resultado advisory
    result = advisory_result(docs)
    elements.append(Paragraph(f"<b>Advisory Result:</b> {result}", styles["Heading2"]))

    # Disclaimer
    elements.append(Paragraph(
        "<i>This report is advisory only. Final operational acceptance remains with the carrier and authorities.</i>",
        styles["Normal"]
    ))

    pdf.build(elements)
    db.close()

    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename="SmartCargo-AIPA-Advisory.pdf"
    )
