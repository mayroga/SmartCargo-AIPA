import os, stripe, httpx, urllib.parse, base64
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Tu configuración de autorización total
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), image_data: Optional[str] = Form(None)):
    instruction = (
        "You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). "
        "Analyze the provided visual evidence. Describe labels, UN codes, and hazards. "
        "Purpose: Prevent fines and holds. Provide direct solutions. "
        "Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    try:
        parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
        
        # LA LLAVE: Procesamos la lectura idéntica que envía el teléfono
        if image_data and "," in image_data:
            # Extraemos los datos puros después de la coma y reparamos posibles espacios
            clean_reading = image_data.split(",")[1].replace(" ", "+").strip()
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": clean_reading
                }
            })

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, json={"contents": [{"parts": parts}]})
            res = r.json()
            
            # Navegación estricta en el JSON para evitar fallos
            if 'candidates' in res and res['candidates'][0]['content']['parts']:
                return {"data": res['candidates'][0]['content']['parts'][0]['text']}
            
            return {"data": "Gemini recibió la lectura pero no pudo extraer texto. Intente una foto más clara."}

    except Exception as e:
        return {"data": f"Error de protocolo técnico: {str(e)}"}

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
