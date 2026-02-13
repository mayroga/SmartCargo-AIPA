from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from models import CargoRequest, AlertLevel, CargoType
import os

# =========================
# APP
# =========================
app = FastAPI(title="SMARTCARGO-AIPA BY MAY ROGA LLC")

# =========================
# Montar carpeta frontend como static (opcional para CSS, JS, imágenes)
# =========================
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# =========================
# MATRIZ DE INCOMPATIBILIDAD IATA
# =========================
INCOMPATIBILITY_MATRIX = {
    "8": ["4.3", "5.1", "5.2"], 
    "4.1": ["5.1", "5.2"],      
    "3": ["5.1", "5.2"],        
    "5.1": ["3", "4.1", "4.2", "4.3", "8"]
}

# =========================
# SERVIR INDEX.HTML
# =========================
@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    # Ruta correcta a tu HTML
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Index.html no encontrado</h1>", status_code=404)

# =========================
# Función de evaluación de carga
# =========================
def evaluate_shipment(req: CargoRequest):
    issues = []
    final_status = AlertLevel.GREEN
    solution = "Carga verificada. Cumple con estándares Avianca Cargo MIA."

    present_classes = [p.dg_class for p in req.pieces if p.dg_class]
    for p_class in present_classes:
        if p_class in INCOMPATIBILITY_MATRIX:
            for other in present_classes:
                if other in INCOMPATIBILITY_MATRIX[p_class]:
                    final_status = AlertLevel.RED
                    issues.append(f"INCOMPATIBILIDAD CRÍTICA: Clase {p_class} y Clase {other} juntas.")
                    solution = "INSTRUCCIÓN: Segregar carga. No pueden compartir pallet o posición."

    for p in req.pieces:
        # Validación PSI
        area = p.length_in * p.width_in
        psi = p.weight_lb / area if area > 0 else 0
        if psi > 200:
            if final_status != AlertLevel.RED:
                final_status = AlertLevel.YELLOW
            issues.append(f"ALERTA PSI: {round(psi,1)} lb/in². Excede límite de piso.")
            solution = "INSTRUCCIÓN: Colocar 'shoring' bajo la carga."

        # Altura para aviones PAX
        if req.aircraft == "PAX" and p.height_in > 63:
            final_status = AlertLevel.RED
            issues.append(f"ALTURA: {p.height_in}in no cabe en avión de Pasajeros.")
            solution = "INSTRUCCIÓN: Reducir altura a 63in o transferir a avión Carguero."

        # Litio SoC >30%
        if p.dg_class == "9" and p.soc_percent and p.soc_percent > 30:
            final_status = AlertLevel.RED
            issues.append("LITIO: Baterías UN3480 con carga > 30%.")
            solution = "INSTRUCCIÓN: Descargar baterías al 30% SoC por seguridad aérea."

    return {"status": final_status, "errors": issues, "action": solution}

# =========================
# Endpoint POST /evaluate
# =========================
@app.post("/evaluate")
async def run_check(req: CargoRequest):
    if not req.is_usa_customer:
        raise HTTPException(status_code=403, detail="Solo disponible para USA")
    return evaluate_shipment(req)

# =========================
# Endpoint GET /evaluate (dummy para navegador)
# =========================
@app.get("/evaluate")
async def evaluate_get_dummy():
    return {"detail": "Para usar este endpoint, enviar POST con JSON a /evaluate"}
