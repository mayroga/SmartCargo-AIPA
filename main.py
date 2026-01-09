import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SmartCargo Advisory by May Roga LLC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================= ENV =================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# ================= STATIC =================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

@app.get("/terms")
async def terms():
    return FileResponse("terms_and_conditions.html")

# ================= CORE ADVISORY =================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    role: Optional[str] = Form("auto")
):
    """
    SMARTCARGO ADVISORY by May Roga LLC - Brain Core
    - SESOR privado: documentación logística, borradores, preguntas estratégicas.
    - Blindaje legal: No autoridad, no certificación, no gobierno.
    """

    core_brain = f"""
SMARTCARGO ADVISORY by May Roga LLC
Official language: {lang}

IDENTIDAD (NO NEGOCIABLE):
- Asesoría logística privada e independiente (SESOR).
- No somos autoridad (DOT, TSA, CBP, IATA). No certificamos.
- Generamos borradores y guías operativas.

MISIÓN CENTRAL:
- Detectar documentos, mercancías y riesgos.
- Generar borradores listos de AWB, B/L, Invoice, Packing List, SLI, etc.
- Formular preguntas abiertas estratégicas si faltan datos.
- Cubrir cualquier escenario: DG, TSA, IATA, DOT, aduanas, mercancías especiales.
- Evitar retrasos y pérdidas.

DOCUMENTOS Y CAMPOS CRÍTICOS:
AWB: Shipper/Consignee, Airport Codes, Weight/Volume, Handling Info (Dry Ice, DG)
Invoice: Incoterm, Currency, Description, Unit Price, HS Code sugerido
Packing List: Net/Gross Weight, Dimensions, Type of Packing, Marks & Numbers

RESUMEN DE CUMPLIMIENTO SESOR:
- SmartCargo proyecta el documento (Draft)
- El cliente revisa y valida
- El cliente firma y oficializa
Esto protege de ser confundido con autoridad o certificador.

REGLAS DE RESPUESTA:
1️⃣ CONTROL – Una línea de calma y dirección
2️⃣ ACTION – Pasos operativos estratégicos
3️⃣ READY TEXT / DRAFT – Borrador completo o mensaje listo
4️⃣ WHY – Impacto operativo (evitar retenciones, retrasos, errores)
5️⃣ CLOSE – Reaseguro de flujo y operación

PREGUNTAS ABIERTAS SI FALTAN DATOS:
- Shipper / Consignee completo
- Airport Codes de origen y destino
- Peso y dimensiones exactas
- ¿Se usa Dry Ice o DG? Indicar cantidad y UN Number / Class
- Clasificación DG si aplica
- Documentos faltantes (AWB, Invoice, Packing List, SLI)
- Requerimientos aduaneros especiales
- Observaciones de transporte (TSA, IATA, DOT, aduanas)
- ¿Alguna instrucción especial de handling o carga?

REGLAS DE LENGUAJE:
❌ illegal, violation, fine, penalty, report, authority, must
✅ recommended step, operational risk, document mismatch, flow optimization, to avoid delays

PHILOSOFÍA:
El cliente paga para que SMARTCARGO piense y actúe. Generamos borradores y preguntas estratégicas, incluso si faltan datos.

CONTEXTO DE SESIÓN:
{prompt}
"""

    guardian_rules = """
FINAL CHECK:
- ¿Generé borradores completos o con placeholders visibles si faltan datos?
- ¿Formulé todas las preguntas estratégicas abiertas necesarias?
- ¿Evité lenguaje legal y de autoridad?
"""

    disclaimer = "\n\nLEGAL NOTE: SmartCargo Advisory by May Roga LLC provides operational drafts and strategic guidance. This is not a legal certification. Final compliance and signatures are the responsibility of the Shipper/User."

    system_prompt = core_brain + guardian_rules + disclaimer

    # ================= GEMINI =================
    if GEMINI_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            )
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(
                    url,
                    json={"contents": [{"parts": [{"text": system_prompt}]}]}
                )
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    return {"data": text}
        except:
            pass

    # ================= OPENAI FALLBACK =================
    if OPENAI_KEY:
        try:
            from openai import AsyncOpenAI
            client_oa = AsyncOpenAI(api_key=OPENAI_KEY)
            res = await client_oa.chat.completions.create(
                model="gpt-4o",
                temperature=0.15,
                messages=[{"role": "system", "content": system_prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            print(f"OpenAI Error: {e}")
            pass

    return {"data": "SMARTCARGO ADVISORY by May Roga LLC is analyzing the situation. Please retry shortly."}

# ================= PAYMENTS =================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    # Bypass para administración
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}"}

    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"SmartCargo Advisory Session – {awb}"},
                    "unit_amount": int(amount * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{DOMAIN_URL}/?access=granted&awb={urllib.parse.quote(awb)}",
            cancel_url=f"{DOMAIN_URL}/"
        )
        return {"url": checkout.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
