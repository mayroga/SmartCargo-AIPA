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

# --- LLAVES DE API ---
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "SmartAdmin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "Ley")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), images: List[UploadFile] = File(None)):
    instruction = (
        f"You are SMARTCARGO CONSULTING. Respond in {lang}. "
        "Provide multiple legal solutions (TSA/IATA/DOT) for cargo compliance. "
        "ORDER: 1. FASTEST & CHEAPEST. 2. Intermediate. 3. Structural/Expensive. "
        "Analyze text and up to 3 photos. Never mention you are an AI."
    )
    
    # --- INTENTO 1: GEMINI (Principal para fotos) ---
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            parts = [{"text": f"{instruction}\n\nClient issue: {prompt}"}]
            if images:
                for img in images[:3]:
                    content = await img.read()
                    if content and len(content) > 0:
                        parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})
            
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=40.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            print(f"Gemini Error: {e}")

    # --- INTENTO 2: OPENAI (Respaldo) ---
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            # OpenAI procesa texto (para fotos requiere lógica adicional, aquí se usa como respaldo de texto)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": response.choices[0].message.content}
        except Exception as e:
            return {"data": f"Critical Error in both AI engines: {e}"}

    return {"data": "API Keys not configured."}

@app.post("/create-payment")
async def payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/index.html?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory AWB {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}

@app.get("/")
async def serve_home():
    return FileResponse("index.html")

app.mount("/", StaticFiles(directory=".", html=True), name="static")
