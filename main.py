# main.py
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.rules import validate_cargo
from backend.ai_helper import advisor_explanation

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")

# -------------------------------
# Seguridad mínima (solo tú)
# -------------------------------

def verify_user(username: str = Form(...), password: str = Form(...)):
    if username != "mayroga" or password != "smartcargo":
        raise HTTPException(status_code=401, detail="Unauthorized")

# -------------------------------
# Static
# -------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return FileResponse(Path("frontend/index.html"))

# -------------------------------
# Validación principal
# -------------------------------

@app.post("/cargo/validate")
async def validate(
    username: str = Form(...),
    password: str = Form(...),
    mawb: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    volume: float = Form(...)
):
    verify_user(username, password)

    cargo = {
        "cargo_type": cargo_type,
        "weight": weight,
        "volume": volume,
        "documents": []  # MVP educativo
    }

    result = validate_cargo(cargo)
    explanation = advisor_explanation(result["semaphore"], result["motivos"])

    result["advisor"] = explanation
    return JSONResponse(result)
