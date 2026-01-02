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
async def home(): return FileResponse("index.html")

@app.get("/success")
async def success(): return FileResponse("success.html")

@app.get("/{file_name}.js")
async def serve_js(file_name: str):
    path = f"{file_name}.js"
    if os.path.exists(path): return FileResponse(path, media_type="application/javascript")
    return HTMLResponse("File not found", status_code=404)

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), images: List[UploadFile] = File(None)):
    # BLINDAJE LEGAL EN LA INSTRUCCIÓN
    instruction = (
        f"You are the Senior Technical Advisor for SMARTCARGO CONSULTING BY MAY ROGA LLC. Answer in {lang}. "
        "IMPORTANT LEGAL SHIELD: We are a PRIVATE ADVISORY firm. We are NOT IATA, NOT TSA, NOT DOT, NOT a government agency. "
        "We do not certify Dangerous Goods and we DO NOT handle or touch the cargo. "
        "Our mission is to provide stability and hope to the logistics chain (Shipper, Forwarder, Driver, Counter, Operator). "
        "Goal: Prevent money loss, cargo holds, delays, and fines. Provide multiple legal solutions. "
        "ORDER: 1. FASTEST & CHEAPEST. 2. INTERMEDIATE. 3. STRUCTURAL. "
        "Identify risks with 🔴 [ALERT] or 🟢 [COMPLIANCE]. Never mention AI."
    )
    
    parts = [{"text": f"{instruction}\n\nClient Issue: {prompt}"}]
    
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            if images:
                for img in images[:3]:
                    content = await img.read()
                    if content: parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error: {str(e)}"}

    return {"data": "System busy. Try again later."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS: return {"url": success_url}
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory AWB: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}

app.mount("/static", StaticFiles(directory="."), name="static")
