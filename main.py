import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Configuración de Identidad
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), cargo_type: str = Form("air"), images: List[UploadFile] = File(None)):
    # Definición de conocimiento legal por modalidad
    laws = {
        "air": "Normativas TSA (ACSP), IATA DGR y seguridad de aviación civil.",
        "land": "Regulaciones USDOT, FMCSA Standard 393 (Cargo Securement) y leyes de Florida.",
        "ocean": "Código IMDG (IMO), regulaciones FMC y protocolos portuarios de Miami/Tampa."
    }
    
    instruction = (
        f"Eres el Asesor Técnico Senior de SMARTCARGO ADVISORY LLC. Responde en {lang}. "
        f"Contexto Legal Actual: {laws.get(cargo_type)}. "
        "TU MISIÓN: Asegurar que la carga pase sin problemas por TSA, Aduanas y Aerolíneas/Navieras. "
        "REGLAS DE RESPUESTA: "
        "1. SEMÁFORO: Usa 🔴 [ALERTA] si hay riesgo de Hold/Rechazo o 🟢 [CUMPLIMIENTO] si es seguro. "
        "2. NADA DE IA: Habla como un consultor humano con 20 años de experiencia en logística de Miami. "
        "3. SOLUCIÓN ÚNICA: Da pasos exactos para rectificar errores de estiba o documentación."
    )
    
    # Motor Principal: Gemini 1.5 Flash (Optimizado para análisis visual de estibas)
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            parts = [{"text": f"{instruction}\n\nConsulta de Carga: {prompt}"}]
            if images:
                for img in images[:3]:
                    content = await img.read()
                    if content: parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    # Motor de Respaldo: OpenAI GPT-4o
    if OPENAI_KEY:
        client = openai.OpenAI(api_key=OPENAI_KEY)
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}])
        return {"data": res.choices[0].message.content}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS: return {"url": success_url}
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Asesoría Técnica: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}

app.mount("/static", StaticFiles(directory="."), name="static")
