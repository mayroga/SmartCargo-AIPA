import os, stripe, httpx, openai, urllib.parse, base64
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Permiso total para que Google Sites pueda enviar fotos a Render sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def advisory_engine(prompt: str = Form(...), image_data: Optional[str] = Form(None)):
    instruction = (
        "You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). PRIVATE TECHNICAL ADVISORS. "
        "Analyze the provided visual evidence. Describe labels, UN codes, and hazards. "
        "Purpose: Prevent fines and holds. No 'audit' words. "
        "Direct solutions. Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    try:
        # Preparamos los componentes de la consulta (Texto + Imagen)
        parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
        
        # Procesamos la "lectura" de la imagen enviada desde Google Sites
        if image_data and "," in image_data:
            # Quitamos el prefijo 'data:image/jpeg;base64,'
            header, encoded_image = image_data.split(",", 1)
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": encoded_image
                }
            })

        # Endpoint de Gemini 1.5 Flash (Soporta Multimodalidad/Visión)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=30.0)
            res = r.json()
            
            if 'candidates' in res and res['candidates'][0]['content']['parts']:
                return {"data": res['candidates'][0]['content']['parts'][0]['text']}
            
            return {"data": "Visual analysis failed or returned empty. Please ensure the photo is clear."}

    except Exception as e:
        return {"data": f"Technical connection error: {str(e)}"}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}&tier={amount}"}
    
    try:
        domain = os.getenv('DOMAIN_URL', 'https://smartcargo-aipa.onrender.com')
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={urllib.parse.quote(awb)}&tier={amount}",
            cancel_url=f"{domain}/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
