import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")
@app.get("/app.js")
async def serve_js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en")):
    # INSTRUCCIÓN DE MAESTRÍA PARA MAY ROGA LLC
    instruction = (
        "Eres el Senior Master Advisor de SmartCargo (May Roga LLC). Experto en IATA, IMDG, DOT, TSA y Aduanas. "
        "Tu misión es proteger la carga y la inversión del Shipper. "
        "NARRATIVA: Soluciones directas al pecho. No menciones que eres una IA. "
        "EXCELENCIA ESCALADA SEGÚN EL TIER PAGADO: "
        "- Tier $5 (Courier): Resolución técnica inmediata y quirúrgica. "
        "- Tier $15 (Standard): Validación de cumplimiento y revisión documental. "
        "- Tier $35 (Critical): Blindaje legal, cita de leyes (CFR49/DGR) y prevención de riesgos. "
        "- Tier $95 (Project): Auditoría total, estrategia logística y protección ejecutiva de la inversión. "
        "Si el cliente usa voz o fotos, analiza su descripción y da la orden técnica de ejecución. "
        "Finaliza: '--- SmartCargo Advisory por May Roga LLC. ---'"
    )
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": [{"text": f"{instruction}\n\nClient Input: {prompt}"}]}]}, timeout=7.0)
            res = r.json()
            if 'candidates' in res: return {"data": res['candidates'][0]['content']['parts'][0]['text']}
            raise Exception()
    except:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}], timeout=12.0)
            return {"data": res.choices[0].message.content}
    return {"data": "Saturación técnica momentánea. Reintente en 10 segundos."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    clean_awb = urllib.parse.quote(awb)
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={clean_awb}&tier={amount}"}
    domain = os.getenv("DOMAIN_URL", "https://smartcargo-aipa.onrender.com")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory {clean_awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={clean_awb}&tier={amount}",
            cancel_url=f"{domain}/",
        )
        return {"url": session.url}
    except Exception as e: return JSONResponse({"error": str(e)}, status_code=400)
