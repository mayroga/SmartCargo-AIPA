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

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(
    action: str = Form(...),
    prompt: str = Form(""),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    # Instrucción Maestra
    base_instruction = f"You are SMARTCARGO CONSULTING. Answer in {lang}. Private logistics consultant. No AI mention."
    
    # Construcción de las PARTES para Gemini (Texto + Imágenes)
    user_parts = []
    
    if action == "inspection":
        user_parts.append({"text": f"{base_instruction}\nACTION: INSPECTION. Analyze files and give a tactical Action Plan.\nContext: {prompt}"})
    else:
        user_parts.append({"text": f"{base_instruction}\nACTION: CONSULTATION. Question: {prompt}"})

    # Procesar archivos a Base64
    if files:
        for f in files:
            content = await f.read()
            if content:
                user_parts.append({
                    "inline_data": {
                        "mime_type": f.content_type,
                        "data": base64.b64encode(content).decode("utf-8")
                    }
                })

    # LLAMADA A GEMINI 1.5 FLASH (Gratis y Multimodal)
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient() as client:
                payload = {"contents": [{"parts": user_parts}]}
                r = await client.post(url, json=payload, timeout=60.0)
                res_j = r.json()
                return {"data": res_j["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            print(f"Gemini Error: {e}")

    # BACKUP OPENAI (Si Gemini falla)
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"{base_instruction} {prompt}"}]
            )
            return {"data": res.choices[0].message.content}
        except: pass

    return {"data": "System busy. Please try again."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')}/?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"AWB: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url=success_url
    )
    return {"url": session.url}

app.mount("/static", StaticFiles(directory="."), name="static")
