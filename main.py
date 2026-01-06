import os, stripe, httpx, openai, urllib.parse, base64
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), image_data: Optional[str] = Form(None)):
    # Instrucciones estrictas para evitar respuestas genéricas
    instruction = (
        f"You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Language: {lang}. "
        "Analyze the provided image data immediately. Describe UN codes and hazards. "
        "If an image is provided, you MUST analyze it visually. Do not say you cannot see it. "
        "Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    try:
        # CONSTRUCCIÓN QUIRÚRGICA DEL CONTENIDO
        # Parte 1: El texto de instrucción
        payload_parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
        
        # Parte 2: La "Lectura" (La clave de Google)
        if image_data and "," in image_data:
            # Extraer base64 puro y asegurar que no tenga espacios corruptos
            b64_string = image_data.split(",")[1].replace(" ", "+").strip()
            payload_parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": b64_string
                }
            })

        # Endpoint de la API 1.5 Flash (El que procesa visión)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json={"contents": [{"parts": payload_parts}]})
            res_json = response.json()
            
            # Si Gemini responde correctamente
            if 'candidates' in res_json:
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                return {"data": answer}
            
            raise ValueError("Respuesta fallida de la API")

    except Exception:
        # Respaldo a OpenAI si Gemini tiene problemas de red
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            res = client_oa.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
    
    return {"data": "Error en el sistema de visión. Contacte a MAY ROGA LLC."}

# Ruta de pagos (Intacta)
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}&tier={amount}"}
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{os.getenv('DOMAIN_URL')}/?access=granted&awb={urllib.parse.quote(awb)}&tier={amount}",
            cancel_url=f"{os.getenv('DOMAIN_URL')}/",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
