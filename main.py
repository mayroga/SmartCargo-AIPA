import os, base64, httpx, openai, stripe
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Configuración de Entorno
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = "https://smartcargo-aipa.onrender.com"

@app.get("/")
async def home(): return FileResponse("index.html")

@app.post("/login-admin")
async def login_admin(user: str = Form(...), password: str = Form(...)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"status": "success"}
    return JSONResponse(status_code=401, content={"status": "denied"})

@app.post("/create-payment")
async def create_payment(price: int = Form(...), lang: str = Form("en")):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': 'SmartCargo Advisory'}, 'unit_amount': price * 100}, 'quantity': 1}],
            mode='payment',
            success_url=f"{DOMAIN}/?status=success&lang={lang}",
            cancel_url=f"{DOMAIN}/?status=cancel",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/advisory")
async def advisory(prompt: str = Form(...), lang: str = Form("en"), images: List[UploadFile] = File(None)):
    # INSTRUCCIÓN MAESTRA CON CRITERIO LEGAL (IATA, TSA, DOT, IMO)
    instruction = (
        f"You are the Senior Compliance Consultant for SmartCargo ADVISORY BY MAY ROGA LLC. Respond strictly in {lang}. "
        "Your goal is to provide stability and hope by ensuring cargo safety. "
        "CRITERIA: Use IATA Dangerous Goods Regulations, TSA Security Standards, DOT Transport rules, and IMO/IMDG maritime codes. "
        "MANDATORY: Identify risks with 🔴 [ALERT] for non-compliance or 🟢 [COMPLIANCE] for safe flow. "
        "NEVER mention AI. Use professional human logic. "
        "LEGAL SHIELD: State that this is a PREVENTIVE ADVICE and NOT an official certification or government inspection."
    )
    
    parts_gemini = [{"text": f"{instruction}\n\nClient Issue: {prompt}"}]
    if images:
        for img in images[:3]:
            content = await img.read()
            if content:
                parts_gemini.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})

    try:
        # Prioridad Gemini 1.5 Flash (Visión Técnica)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": parts_gemini}]}, timeout=45.0)
            return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
    except:
        # Respaldo OpenAI GPT-4o
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}])
        return {"data": res.choices[0].message.content}
