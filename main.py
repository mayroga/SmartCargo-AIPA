# main.py
import os
import time
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import CargoRequest, CargoEvaluation, AlertLevel, CargoPiece, Role
from backend.ai_helper import query_ai
from pathlib import Path

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# UTILS
# =========================
def evaluate_piece(piece: CargoPiece) -> CargoEvaluation:
    alert = AlertLevel.GREEN
    notes = ""

    # DG rules
    if piece.cargo_type == "DG":
        if piece.weight_kg > 400:  # kg limit per DG piece
            alert = AlertLevel.RED
            notes += "⚠️ DG weight exceeds limit.\n"
        if piece.height_m and piece.height_m > 2.5:
            alert = AlertLevel.YELLOW
            notes += "⚠️ DG height exceeds standard ULD limit.\n"

    # PHARMA / PERISHABLE rules
    if piece.cargo_type in ["PHARMA", "PERISHABLE"]:
        if piece.temperature_c is None:
            alert = AlertLevel.RED
            notes += "⚠️ Temperature info missing.\n"
        elif piece.temperature_c > 8:
            alert = AlertLevel.YELLOW
            notes += "⚠️ Temperature exceeds recommended limit.\n"

    # HUMAN REMAINS
    if piece.cargo_type == "HUMAN_REMAINS":
        if piece.weight_kg > 200:
            alert = AlertLevel.YELLOW
            notes += "⚠️ Weight exceeds standard container recommendation.\n"

    # FULL PALLET / OVERLIMIT
    if piece.cargo_type == "FULL_PALLET":
        if piece.height_m and piece.height_m > 2.5:
            alert = AlertLevel.YELLOW
            notes += "⚠️ Pallet height exceeds limit.\n"

    # GENERAL cargo: check oversized
    if piece.cargo_type == "GENERAL":
        if piece.height_m and piece.height_m > 3:
            alert = AlertLevel.YELLOW
            notes += "⚠️ Piece is oversized.\n"

    if notes == "":
        notes = "✅ Piece within normal limits."

    return CargoEvaluation(piece_id=piece.id, alert=alert, observation=notes)

# =========================
# EVALUATE ENTIRE SHIPMENT
# =========================
@app.post("/evaluate")
async def evaluate_shipment(cargo: CargoRequest):
    results = []

    for piece in cargo.pieces:
        eval_piece = evaluate_piece(piece)
        results.append(eval_piece.dict())

    # AI observations: send entire shipment summary
    ai_prompt = f"Analyze the following cargo shipment and give concrete observations and recommendations:\n{cargo.dict()}"
    try:
        ai_observation = query_ai(ai_prompt)
    except Exception as e:
        ai_observation = f"AI could not process: {str(e)}"

    return JSONResponse({
        "results": results,
        "ai_observation": ai_observation
    })

# =========================
# UPLOAD DOCUMENTS
# =========================
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "path": str(save_path)}

# =========================
# FRONTEND ENTRY
# =========================
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()
