from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pdfkit

app = FastAPI()

# Carpeta para archivos estáticos (JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# --- CASCADA DE DECISIONES (Lógica Letal) ---
def evaluar_carga(tipo_carga, avion, alto_cm, peso_guia, peso_real, dg_firmado, madera_nimf, temp_rango):
    """
    Retorna:
    {
        "semaforo": "ROJO/AMARILLO/VERDE",
        "mensaje": "Texto explicativo",
        "solucion": "Acción sugerida"
    }
    """
    semaforo = "VERDE"
    mensaje = []
    solucion = []

    # 1️⃣ Trigger: Tipo de Carga
    if tipo_carga.lower() == "dg":
        # Bloques: Declaración DGD, Etiquetas UN, Clase de Riesgo
        if not dg_firmado:
            semaforo = "ROJO"
            mensaje.append("DGD no firmado. Carga NO RECIBIDA")
            solucion.append("Solicitar DGD firmado antes de recibir")
    elif tipo_carga.lower() == "perecederos":
        # Bloques: Temperatura, Registro de Sensor, Tipo de Hielo
        if temp_rango != "ok":
            semaforo = "ROJO"
            mensaje.append("Temperatura fuera de rango")
            solucion.append("Verificar cadena de frío antes de aceptar")
    
    # 2️⃣ Compatibilidad avión
    if avion.lower() == "belly/pax" and alto_cm > 80:
        semaforo = "ROJO"
        mensaje.append("Dimensión excede 80cm en Belly/PAX")
        solucion.append("Transferir a Freighter o re-estibar")
    
    # 3️⃣ Peso real vs guía
    if abs(peso_guia - peso_real)/peso_guia > 0.02:
        if semaforo != "ROJO":
            semaforo = "AMARILLO"
        mensaje.append(f"Diferencia de peso >2% (Guía: {peso_guia}, Real: {peso_real})")
        solucion.append("Corregir guía o re-tarifar")
    
    # 4️⃣ Madera NIMF-15
    if madera_nimf == "no":
        if semaforo != "ROJO":
            semaforo = "AMARILLO"
        mensaje.append("Madera sin sello NIMF-15")
        solucion.append("Cambiar a plástico o re-palettizar y fumigar")
    
    # 5️⃣ Default
    if not mensaje:
        mensaje.append("Carga apta para vuelo")
        solucion.append("Proceder a zona de armado")
    
    return {
        "semaforo": semaforo,
        "mensaje": mensaje,
        "solucion": solucion
    }

# --- RUTAS ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/evaluar_carga")
def evaluar(
    tipo_carga: str = Form(...),
    avion: str = Form(...),
    alto_cm: float = Form(...),
    peso_guia: float = Form(...),
    peso_real: float = Form(...),
    dg_firmado: str = Form(...),  # "yes"/"no"
    madera_nimf: str = Form(...),  # "yes"/"no"
    temp_rango: str = Form(...),   # "ok"/"fuera"
):
    resultado = evaluar_carga(
        tipo_carga, avion, alto_cm, peso_guia, peso_real,
        dg_firmado.lower() == "yes",
        madera_nimf.lower(),
        temp_rango.lower()
    )
    return JSONResponse(resultado)

@app.post("/generar_pdf")
def generar_pdf(request: Request):
    """
    Recibe JSON con la evaluación y genera PDF certificado
    """
    data = request.json()
    semaforo = data.get("semaforo", "")
    mensaje = "<br>".join(data.get("mensaje", []))
    solucion = "<br>".join(data.get("solucion", []))
    numero_vuelo = data.get("vuelo", "No asignado")

    html_pdf = f"""
    <html>
    <head><title>Certificado de Conformidad</title></head>
    <body>
    <h2>Carga Aptada para Vuelo AV {numero_vuelo}</h2>
    <p>Validado bajo normas IATA/TSA</p>
    <p><strong>Estatus: {semaforo}</strong></p>
    <p><strong>Observaciones:</strong><br>{mensaje}</p>
    <p><strong>Acción sugerida:</strong><br>{solucion}</p>
    <hr>
    <small>Nota Legal: Este reporte constituye asesoría técnica preventiva. May Roga LLC no se responsabiliza por decisiones de CBP, TSA, DOT o aerolíneas.</small>
    </body>
    </html>
    """
    pdf = pdfkit.from_string(html_pdf, False)
    return HTMLResponse(content=pdf, media_type="application/pdf")
