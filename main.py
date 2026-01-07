import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Configuración de CORS para que la App responda desde cualquier lugar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Sincronización con tus variables de Render
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), image_data: Optional[str] = Form(None)):
    # INSTRUCCIÓN MAESTRA: EL GENERAL DE LOGÍSTICA (MAY ROGA LLC)
    instruction = (
        f"You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Language: {lang}. "
        "URGENT: Stop acting like a textbook. You are a Tactical Logistics General. "
        "Your mission is to provide EXECUTIVE SOLUTIONS, not study tasks. "
        
        "STRUCTURE OF YOUR RESPONSE:"
        "1. DIRECT DIAGNOSIS: Tell the client EXACTLY what is happening (e.g., 'You have Class 3 DG' or 'Your AWB is missing a signature'). "
        "2. WHERE TO LOOK: Tell them exactly where to look (e.g., 'Check Section 14 of SDS', 'Search for the diamond label on the box'). "
        "3. THREE ACTIONABLE SOLUTIONS: "
        "   - SOLUTION A (Immediate Action): What to do right now to fix the physical or document error. "
        "   - SOLUTION B (Compliance/Legal): How to avoid the 'Hold' or fine from TSA, CBP or DOT. "
        "   - SOLUTION C (Master Advice): A professional 'trick' or strategic move to protect their money. "
        
        "STRICT RULES:"
        "- DO NOT say 'it is important to verify'. Say 'Verify this now'. "
        "- DO NOT suggest 'training'. Suggest 'Demand the correct document from the shipper'. "
        "- If a photo is provided, ANALYZE it first. If it is blurry, INTERROGATE for UN codes, weights, or cargo types. "
        "- We are PRIVATE. NOT GOVERNMENT. "
        "Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    res_final = {"data": "SYSTEM: No data received. Please describe your cargo/documents by voice or text.", "image": image_data}

    try:
        # PLAN A: GEMINI 1.5 FLASH (Cerebro Principal)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
        
        if image_data and "," in image_data:
            # Limpieza de Base64 para evitar errores de red
            b64_clean = image_data.split(",")[1].replace(" ", "+").strip()
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64_clean}})

        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(url, json={
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "maxOutputTokens": 600,
                    "temperature": 0.1 # Alta precisión, cero alucinaciones
                }
            })
            j = r.json()
            if "candidates" in j and len(j["candidates"]) > 0:
                res_final["data"] = j['candidates'][0]['content']['parts'][0]['text']
                return res_final
    except Exception as e:
        print(f"Gemini Error: {e}")

    try:
        # PLAN B: OPENAI GPT-4o (Respaldo Automático)
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            content_list = [{"type": "text", "text": instruction + "\n" + prompt}]
            if image_data:
                content_list.append({"type": "image_url", "image_url": {"url": image_data}})
            
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content_list}],
                max_tokens=600
            )
            res_final["data"] = res.choices[0].message.content
            return res_final
    except Exception as e:
        res_final["data"] = f"TECHNICAL CONNECTION ERROR. USE VOICE/TEXT: {str(e)}"
    
    return res_final

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    # Lógica de Acceso Maestro (Tú entras gratis)
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"./?access=granted&awb={urllib.parse.quote(awb)}&monto=0"}
    
    # Lógica de Stripe (Los clientes pagan)
    try:
        domain = os.getenv('DOMAIN_URL', 'https://smartcargo-aipa.onrender.com')
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Advisory Ref: {awb}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={urllib.parse.quote(awb)}&monto={amount}",
            cancel_url=f"{domain}/",
        )
        return {"url": checkout_session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
