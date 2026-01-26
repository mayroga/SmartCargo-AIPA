import os
import json
import httpx
from fastapi import FastAPI, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db
from models import Cargo, Document
from datetime import datetime

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar Base de Datos
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuración de Claves
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

async def advisor_engine(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.post(url, json=payload)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")

@app.post("/validate")
async def validate_cargo(
    mawb: str = Form(...),
    hawb: str = Form(None),
    role: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    length: float = Form(...),
    width: float = Form(...),
    height: float = Form(...),
    dot: str = Form(...),
    db: Session = Depends(get_db)
):
    volume = round((length * width * height) / 1_000_000, 3)
    
    # --- REGLAS TÉCNICAS AVIANCA / IATA ---
    status = "GREEN"
    technical_notes = []
    
    # Límite de altura para aviones de pasajeros (Belly Cargo)
    if height > 114 and height <= 160:
        technical_notes.append("REQUIRES WIDE-BODY AIRCRAFT (A330/B787). Cannot fit in A320 family.")
        status = "YELLOW"
    elif height > 160:
        technical_notes.append("CARGO AIRCRAFT ONLY (A330F). Exceeds passenger belly height limits.")
        status = "RED" if height > 244 else "YELLOW"

    if cargo_type.upper() in ["DG", "HAZMAT"] and dot.upper() != "YES":
        status = "RED"
        technical_notes.append("CRITICAL: DOT Declaration missing for Dangerous Goods.")

    # Guardar en DB para trazabilidad
    new_cargo = Cargo(
        mawb=mawb, hawb=hawb, origin=origin, destination=destination,
        cargo_type=cargo_type, weight_kg=weight, length_cm=length,
        width_cm=width, height_cm=height, role=role
    )
    db.add(new_cargo)
    db.commit()

    # --- PROMPT DE EXPERTO (SMARTCARGO-AIPA) ---
    prompt = f"""
    Eres SMARTCARGO-AIPA by May Roga LLC. Experto en regulaciones de Avianca, IATA, TSA, CBP y DOT.
    Analiza esta carga:
    - MAWB: {mawb} | Rol: {role}
    - Tipo: {cargo_type} | DOT Declared: {dot}
    - Dims: {length}x{width}x{height} cm | Peso: {weight} kg
    - Origen/Destino: {origin} to {destination}
    - Notas Técnicas: {technical_notes}

    INSTRUCCIONES:
    1. Responde de forma breve pero con mucho peso.
    2. Usa TABLAS para mostrar requerimientos de papelería oficial.
    3. Cita normativas IATA/TSA/CBP de forma autoritaria.
    4. NO digas que eres una IA.
    5. Si la carga es peligrosa, especifica los documentos de seguridad necesarios.
    6. Incluye siempre la cláusula de protección legal.
    """

    advisor_response = await advisor_engine(prompt)

    return JSONResponse({
        "status": status,
        "volume": volume,
        "notes": technical_notes,
        "analysis": advisor_response,
        "legal_notice": "SMARTCARGO-AIPA by May Roga LLC. Preventive documentary validation. Not a government authority. Airline decision is final."
    })
