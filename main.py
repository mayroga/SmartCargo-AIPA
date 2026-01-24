from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import tempfile
import os

# PDF
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# DB
from backend.models import Base, engine, SessionLocal, Cargo, Document


# Rules
from backend.rules import validate_cargo, advisory_result

# Storage
from storage import save_document

# -------------------- APP --------------------
app = FastAPI(title="SmartCargo-AIPA")

Base.metadata.create_all(bind=engine)

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
    hawb: str = Form(""),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    flight_date: str = Form(...)
):
    db = SessionLocal()

    cargo = Cargo(
        mawb=mawb,
        hawb=hawb,
        origin=origin,
        destination=destination,
        cargo_type=cargo_type,
        flight_date=flight_date
    )

    db.add(cargo)
    db.commit()
    db.refresh(cargo)
    db.close()

    return {"cargo_id": cargo.id}


@app.get("/cargo/all")
def list_cargos():
    db = SessionLocal()
    cargos = db.query(Cargo).all()
    result = []

    for c in cargos:
        docs = db.query(Document).filter(Document.cargo_id == c.id).all()
        result.append({
            "id": c.id,
            "mawb": c.mawb,
            "hawb": c.hawb,
            "origin": c.origin,
            "destination": c.destination,
            "cargo_type": c.cargo_type,
            "flight_date": str(c.flight_date),
            "documents": [
                {
                    "type": d.doc_type,
                    "version": d.version,
                    "status": d.status,
                    "responsible": d.responsible,
                    "audit_notes": d.audit_notes,
                    "upload_date": str(d.upload_date)
                } for d in docs
            ]
        })

    db.close()
    return result


# -------------------- DOCUMENTS --------------------
@app.post("/cargo/upload")
def upload_document(
    cargo_id: int = Form(...),
    doc_type: str = Form(...),
    responsible: str = Form(...),
    file: UploadFile = File(...)
):
    db = SessionLocal()

    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        db.close()
        raise HTTPException(status_code=404, detail="Cargo not found")

    doc = save_document(db, cargo_id, doc_type, responsible, file)
    db.close()

    return {"status": "uploaded", "version": doc.version}


# -------------------- PDF ASESOR --------------------
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

    elements.append(Paragraph(
        "<b>SmartCargo-AIPA by May Roga LLC</b>",
        styles["Title"]
    ))

    elements.append(Paragraph(
        "Cargo Documentation Advisory Report<br/><br/>",
        styles["Normal"]
    ))

    elements.append(Paragraph(
        f"<b>MAWB:</b> {cargo.mawb}<br/>"
        f"<b>Origin:</b> {cargo.origin} → {cargo.destination}<br/>"
        f"<b>Type:</b> {cargo.cargo_type}<br/><br/>",
        styles["Normal"]
    ))

    table_data = [["Document", "Version", "Status", "Responsible", "Audit Notes"]]

    for d in docs:
        table_data.append([
            d.doc_type,
            d.version,
            d.status.upper(),
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

    result = advisory_result(docs)

    elements.append(Paragraph(
        f"<b>Advisory Result:</b> {result}",
        styles["Heading2"]
    ))

    elements.append(Paragraph(
        "<i>This report is advisory only. Final acceptance remains with the carrier and authorities.</i>",
        styles["Normal"]
    ))

    pdf.build(elements)
    db.close()

    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename="SmartCargo-AIPA-Advisory.pdf"
    )
