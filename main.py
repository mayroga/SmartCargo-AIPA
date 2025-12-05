from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil

app = FastAPI(title="SmartCargo-AIPA Backend")

# ================= CORS =================
frontend_origin = "https://smartcargo-advisory.onrender.com"  # URL de tu Static Site
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= UPLOAD DIRECTORY =================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ================= RUTAS =================
@app.get("/")
async def root():
    return {"message":"SmartCargo-AIPA Backend activo","mode":"free","routes":["/cargas","/upload","/advisory","/simulacion","/create-payment"]}

# --------- CARGAS ----------
cargas_db = []  # Ejemplo en memoria
@app.get("/cargas")
async def get_cargas():
    return cargas_db

@app.post("/cargas")
async def create_carga(carga: dict):
    carga_id = len(cargas_db) + 1
    carga["id"] = carga_id
    cargas_db.append(carga)
    return {"id": carga_id, "status":"ok"}

# --------- UPLOAD DOCUMENTS ----------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"data": {"filename": file.filename, "url": f"/files/{file.filename}"}}

# --------- SERVE FILES ----------
@app.get("/files/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# --------- ADVISORY ----------
@app.post("/advisory")
async def advisory(question: dict):
    # Ejemplo de respuesta simulada
    q = question.get("question", "")
    return {"data": f"Respuesta simulada a: {q}"}

# --------- SIMULACION ----------
@app.get("/simulacion/{tipo}/{count}")
async def simulacion(tipo: str, count: int):
    riesgo = min(count * 10, 100)
    return {"riesgo_rechazo": f"{riesgo}%"}

# --------- CREATE PAYMENT ----------
@app.post("/create-payment")
async def create_payment(amount: int = 0, description: str = ""):
    return {"message": f"Pago simulado: {description} — ${amount/100}"}
