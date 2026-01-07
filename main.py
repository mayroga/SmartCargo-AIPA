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
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), image_data: Optional[str] = Form(None)):
    instruction = (
        f"You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Language: {lang}. "
        "Strict Rule: We are PRIVATE consultants. We are NOT government (NOT TSA, NOT CBP, NOT DOT). "
        "Provide direct technical solutions for cargo safety and compliance to avoid fines. "
        "Analyze image, voice, or text. Be precise. No auditing. "
        "End with: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    )
    
    res_final = {"data": "SYSTEM ERROR: Describe cargo by text/voice.", "image": image_data}

    try:
        # PLAN A: GEMINI
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        parts = [{"text": f"{instruction}\n\nCase: {prompt}"}]
        if image_data and "," in image_data:
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data.split(",")[1].replace(" ", "+")}})

        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(url, json={"contents": [{"parts": parts}]})
            j = r.json()
            if "candidates" in j:
                res_final["data"] = j['candidates'][0]['content']['parts'][0]['text']
                return res_final
    except:
        # PLAN B: OPENAI
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            content = [{"type": "text", "text": instruction + "\n" + prompt}]
            if image_data: content.append({"type": "image_url", "image_url": {"url": image_data}})
            res = client_oa.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": content}])
            res_final["data"] = res.choices[0].message.content
            return res_final
    
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
