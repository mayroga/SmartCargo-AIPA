from fastapi import FastAPI, HTTPException
from models import CargoRequest, AlertLevel, CargoType

app = FastAPI(title="SmartCargo-AIPA Industrial")

# MATRIZ DE INCOMPATIBILIDAD IATA (Segregación)
# Determina qué clases NO pueden viajar juntas en el mismo ULD/Pallet
INCOMPATIBILITY_MATRIX = {
    "8": ["4.3", "5.1", "5.2"], # Corrosivos no con reactivos al agua o comburentes
    "4.1": ["5.1", "5.2"],      # Sólidos inflamables no con comburentes
    "3": ["5.1", "5.2"],        # Líquidos inflamables no con comburentes
    "5.1": ["3", "4.1", "4.2", "4.3", "8"] # Comburentes son altamente incompatibles
}

def evaluate_shipment(req: CargoRequest):
    issues = []
    final_status = AlertLevel.GREEN
    solution = "Carga verificada. Cumple con estándares Avianca Cargo MIA."
    
    # 1. Validación de Segregación DG
    present_classes = [p.dg_class for p in req.pieces if p.dg_class]
    for p_class in present_classes:
        if p_class in INCOMPATIBILITY_MATRIX:
            for other in present_classes:
                if other in INCOMPATIBILITY_MATRIX[p_class]:
                    final_status = AlertLevel.RED
                    issues.append(f"INCOMPATIBILIDAD CRÍTICA: Clase {p_class} y Clase {other} juntas.")
                    solution = "INSTRUCCIÓN: Segregar carga. No pueden compartir pallet o posición."

    for p in req.pieces:
        # 2. Validación de PSI (Pounds per Square Inch)
        area = p.length_in * p.width_in
        psi = p.weight_lb / area if area > 0 else 0
        if psi > 200: # Límite estructural estándar
            if final_status != AlertLevel.RED: final_status = AlertLevel.YELLOW
            issues.append(f"ALERTA PSI: {round(psi,1)} lb/in². Excede límite de piso.")
            solution = "INSTRUCCIÓN: Colocar 'shoring' (madera de distribución) bajo la carga."

        # 3. Validación de Contorno y Altura
        if req.aircraft == "PAX" and p.height_in > 63:
            final_status = AlertLevel.RED
            issues.append(f"ALTURA: {p.height_in}in no cabe en avión de Pasajeros.")
            solution = "INSTRUCCIÓN: Reducir altura a 63in o transferir a avión Carguero puro."

        # 4. Litio SoC 30%
        if p.dg_class == "9" and p.soc_percent and p.soc_percent > 30:
            final_status = AlertLevel.RED
            issues.append("LITIO: Baterías UN3480 con carga > 30%.")
            solution = "INSTRUCCIÓN: Descargar baterías al 30% SoC por seguridad aérea."

    return {"status": final_status, "errors": issues, "action": solution}

@app.post("/evaluate")
async def run_check(req: CargoRequest):
    if not req.is_usa_customer:
        raise HTTPException(status_code=403, detail="Solo disponible para USA")
    return evaluate_shipment(req)
