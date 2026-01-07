import os, httpx, stripe, urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")
@app.get("/app.js")
async def js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory(prompt:str=Form(""), image_data:str=Form(""), lang:str=Form("auto")):
    system = """
You are SmartCargo Advisory AI by MAY ROGA LLC.

Detect:
- Cargo damage
- Labels & markings
- UN codes
- Documents (AWB, BL, Invoice, Packing List)
Provide advisory only.
No execution. No issuing documents.
Language: AUTO DETECT.
Finish with disclaimer.
"""
    parts = []
    if "," in image_data:
        h,d = image_data.split(",",1)
        parts.append({"inline_data":{"mime_type":h.split(";")[0].replace("data:",""),"data":d}})
    parts.append({"text":system+"\nClient:"+prompt})

    url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    async with httpx.AsyncClient() as c:
        r = await c.post(url,json={"contents":[{"parts":parts}]})
        res = r.json()
        text="".join(p.get("text","") for p in res["candidates"][0]["content"]["parts"])
        detected = "es" if " el " in text.lower() else "en"
        return {"data":text,"lang":detected}

@app.post("/translate")
async def translate(text:str=Form(...), target:str=Form(...)):
    return {"text":text,"lang":target}

@app.post("/create-payment")
async def pay(amount:float=Form(...), awb:str=Form(...), user:str=Form(None), password:str=Form(None)):
    if user==ADMIN_USER and password==ADMIN_PASS:
        return {"url":"/?access=granted"}
    domain=os.getenv("DOMAIN_URL")
    s=stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data":{"currency":"usd","product_data":{"name":"SmartCargo Advisory"},"unit_amount":int(amount*100)},"quantity":1}],
        mode="payment",
        success_url=f"{domain}/?access=granted",
        cancel_url=f"{domain}/"
    )
    return {"url":s.url}
