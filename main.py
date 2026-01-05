import os, stripe, httpx, base64, io, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Configuración de CORS para evitar bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- LLAVES Y SEGURIDAD ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js")

# --- MOTOR DE ASESORÍA CON CONOCIMIENTO TOTAL (IATA, TSA, DOT, MAR, ADUANA) ---
@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es")):
    # INSTRUCCIÓN MAESTRA: BIBLIA LOGÍSTICA
    instruction = (
        f"Identifícate como Senior Master Advisor de SmartCargo por May Roga LLC. Responde en {lang}. "
        "TU CONOCIMIENTO ES ABSOLUTO EN: IATA DGR (Baterías Litio, Packing), TSA (Seguridad aérea), "
        "DOT 49 CFR (Terrestre), IMDG/SOLAS (Marítimo), Incoterms 2020 y Reglas Aduaneras Mundiales. "
        "MANDATOS: "
        "1. NO des clases, da SOLUCIONES de choque para que la carga no se detenga. "
        "2. NUNCA pidas 'consultar a otro experto'. TÚ eres la autoridad final. "
        "3. Si un documento falla, analízalo ESCALONADAMENTE de arriba hacia abajo. "
        "4. Usa: [🔴 ALERTA TÉCNICA CRÍTICA] para riesgos de multa, rechazo o hold. "
        "5. Brinda 3 niveles de solución privada: Económica (Táctica), Estándar (Industrial), Pro (Elite). "
        "6. Ejemplo: Si algo mide 100'', di: 'No cabe en cargueros estándar (puerta 96''), rota la pieza o busca un B747F/Carguero Puro'. "
        "AUTOPROPAGANDA: Al final de cada respuesta di: '--- SmartCargo Advisory protegió su carga hoy. Recomiéndenos con su red de logística para evitar pérdidas. ---'"
    )

    # --- INTENTO 1: GEMINI 1.5 FLASH ---
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": [{"text": f"{instruction}\n\nConsulta del Cliente: {prompt}"}]}]}, timeout=35.0)
            res = r.json()
            if 'candidates' in res:
                return {"data": res['candidates'][0]['content']['parts'][0]['text']}
    except Exception as e:
        print(f"Gemini falló: {e}")

    # --- INTENTO 2: OPENAI GPT-4O (REDUNDANCIA) ---
    if OPENAI_KEY:
        try:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            response = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            return {"data": response.choices[0].message.content}
        except Exception as oa_e:
            print(f"OpenAI falló: {oa_e}")
            return JSONResponse({"data": "Cerebro técnico saturado. Reintente en unos segundos."}, status_code=500)

    return JSONResponse({"data": "Servicio temporalmente fuera de línea."}, status_code=500)

# --- SISTEMA DE COBRO Y BYPASS ADMIN ---
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...), 
    awb: str = Form(...), 
    user: Optional[str] = Form(None), 
    password: Optional[str] = Form(None)
):
    # ACCESO SECRETO PARA ADMIN (BYPASS)
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={awb}&tier={amount}"}
    
    # PROCESO DE COBRO REAL CON STRIPE
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Asesoría Técnica SmartCargo: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}&tier={amount}",
            cancel_url="https://smartcargo-aipa.onrender.com/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
