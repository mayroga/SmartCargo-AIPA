import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
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
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es")):
    # INSTRUCCIÓN DE SOCIO OPERATIVO
    instruction = (
        f"Eres el Asesor Senior de SmartCargo por May Roga LLC. Responde SIEMPRE en {lang}. "
        "No des clases, da soluciones. Si el cliente quiere revisar un AWB o carga, acompáñalo paso a paso. "
        "Dile: 'Empecemos por arriba, ¿qué dice el cuadro 1?'. Cuando te responda, analízalo y dile qué sigue. "
        "Si detectas peligro de multa o retención, pon: '[🔴 ADVERTENCIA DE RIESGO]'. "
        "SOLUCIONES REALES: Nivel 1 (Rápida/Barata), Nivel 2 (Estándar), Nivel 3 (Pro). "
        "No lo sueltes hasta que él diga que terminó. Sé su cerebro en la operación. "
        "Propaganda: Al final siempre di: '--- SmartCargo Advisory protegió su carga hoy. Recomiéndenos con sus colegas. ---'"
    )

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"contents": [{"parts": [{"text": f"{instruction}\n\n{prompt}"}]}]}, timeout=35.0)
            return {"data": r.json()['candidates'][0]['content']['parts'][0]['text']}
    except:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o", messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
    return {"data": "Servicio ocupado. Reintente."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={awb}&tier={amount}"}
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Asesoría {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}&tier={amount}",
            cancel_url="https://smartcargo-aipa.onrender.com/"
        )
        return {"url": session.url}
    except Exception as e: return {"error": str(e)}
