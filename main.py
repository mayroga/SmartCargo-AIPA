# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pathlib import Path
from backend.rules import validate_cargo
from backend.ai_helper import advisor_explanation
import secrets

app = FastAPI(title="SMARTCARGO-AIPA by May Roga LLC")
security = HTTPBasic()

USERNAME = "mayroga"
PASSWORD = "smartcargo2026"

def auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not (
        secrets.compare_digest(credentials.username, USERNAME)
        and secrets.compare_digest(credentials.password, PASSWORD)
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/", dependencies=[Depends(auth)])
def index():
    return FileResponse(Path("frontend/index.html"))

@app.post("/cargo/validate", dependencies=[Depends(auth)])
def cargo_validate(
    mawb: str = Form(...),
    cargo_type: str = Form(...),
    weight: float = Form(...),
    volume: float = Form(...),
):
    cargo = {
        "mawb": mawb,
        "cargo_type": cargo_type,
        "weight": weight,
        "volume": volume,
        "documents": []  # documentos evaluados en frontend
    }
    return JSONResponse(validate_cargo(cargo))

@app.get("/advisor/explain", dependencies=[Depends(auth)])
def advisor(code: str, lang: str = "en"):
    return {
        "advisor": "Asesor SmartCargo-AIPA",
        "message": advisor_explanation(code, lang)
    }
