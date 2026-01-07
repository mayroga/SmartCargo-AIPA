import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Sincronización exacta con tus variables de Render
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY") # Ajustado a tu lista
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")
@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), image_data: Optional[str] = Form(None)):
    # Instrucción Maestra: El Cerebro de MAY ROGA LLC
    instruction = (
        f"You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Language: {lang}. "
        "Your mission is to analyze logistics risks (BEFORE, DURING, AFTER). "
        "Strict Rule: We are PRIVATE consultants. NOT government (NOT TSA, NOT CBP, NOT DOT). "
        "If the image is not clear or missing, PROACTIVELY ask for details: Cargo type, Destination, UN codes, or Document types. "
        "Provide 3 technical solutions to avoid holds and fines. No auditing. "
        "End with: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    res_final = {"data": "SYSTEM: Please describe your documents or cargo via voice/text for analysis.", "image": image_data}

    try:
        # PLAN A: GEMINI 1.5 FLASH (Protocolo de Visión Correcto)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        parts = [{"text": f"{instruction}\n\nClient Input: {prompt}"}]
        
        if image_data and "," in image_data:
            b64_data = image_data.split(",")[1].replace(" ", "+").strip()
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64_data}})

        async with httpx.AsyncClient(timeout=40.0) as client:
            r = await client.post(url, json={"contents": [{"parts": parts}], "generationConfig": {"maxOutputTokens": 500, "temperature": 0.2}})
            j = r.json()
            if "candidates" in j and len(j["candidates"]) > 0:
                res_final["data"] = j['candidates'][0]['content']['parts'][0]['text']
                return res_final
    except Exception as e:
        print(f"Gemini Error: {e}")

    try:
        # PLAN B: OPENAI GPT-4o (Respaldo)
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            content_list = [{"type": "text", "text": instruction + "\n" + prompt}]
            if image_data:
                content_list.append({"type": "image_url", "image_url": {"url": image_data}})
            
            res = client_oa.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": content_list}], max_tokens=500)
            res_final["data"] = res.choices[0].message.content
            return res_final
    except Exception as e:
        res_final["data"] = f"Technical Connection Error. Please use Voice/Text: {str(e)}"
    
    return res_final

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": f"./?access=granted&awb={urllib.parse.quote(awb)}&monto=0"}
    try:
        domain = os.getenv('DOMAIN_URL', 'https://smartcargo-aipa.onrender.com')
        s = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={urllib.parse.quote(awb)}&monto={amount}",
            cancel_url=f"{domain}/"
        )
        return {"url": s.url}
    except Exception as e: return JSONResponse({"error": str(e)}, status_code=400)
