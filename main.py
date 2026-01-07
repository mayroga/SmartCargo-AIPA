import os, stripe, httpx, openai, urllib.parse
from fastapi import FastAPI, Form
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
    allow_headers=["*"]
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")
@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

def parse_ai_response(j): 
    text=""; 
    if "candidates" in j:
        for c in j["candidates"]:
            if "content" in c:
                for p in c["content"].get("parts",[]):
                    if "text" in p: text+=p["text"]+"\n"
    elif "choices" in j:
        try: text+=j["choices"][0]["message"]["content"]
        except: pass
    return text.strip()

@app.post("/advisory")
async def advisory_engine(prompt:str=Form(...),lang:str=Form("en"),image_data:Optional[str]=Form(None)):
    instruction = f"You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Language: {lang}. Provide EXECUTIVE SOLUTIONS only.\nSTRUCTURE:\n1. DIRECT DIAGNOSIS\n2. WHERE TO LOOK\n3. THREE ACTIONABLE SOLUTIONS\nRULES:\n- Be direct. No theory.\n- PRIVATE.\n--- SmartCargo Advisory by MAY ROGA LLC ---"
    result={"data":"SYSTEM: No data received","image":None}

    try: # GEMINI
        url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        parts=[{"text":f"{instruction}\n\nClient Input: {prompt}"}]
        async with httpx.AsyncClient(timeout=45) as client:
            r=await client.post(url,json={"contents":[{"parts":parts}],"generationConfig":{"maxOutputTokens":600,"temperature":0.1}})
            t=parse_ai_response(r.json())
            if t: result["data"]=t
            return result
    except: pass

    try: # OPENAI backup
        if OPENAI_KEY:
            client_oa=openai.OpenAI(api_key=OPENAI_KEY)
            content=[{"type":"text","text":instruction+"\n"+prompt}]
            res=client_oa.chat.completions.create(model="gpt-4o",messages=[{"role":"user","content":content}],max_tokens=600)
            t=parse_ai_response(res.to_dict())
            if t: result["data"]=t
    except Exception as e: result["data"]=f"TECH ERROR: {str(e)}"

    return result

@app.post("/create-payment")
async def create_payment(amount:float=Form(...),awb:str=Form(...),user:Optional[str]=Form(None),password:Optional[str]=Form(None)):
    if user==ADMIN_USER and password==ADMIN_PASS:
        return {"url":f"./?access=granted&awb={urllib.parse.quote(awb)}&monto=0"}
    try:
        domain=os.getenv("DOMAIN_URL","https://smartcargo-aipa.onrender.com")
        checkout=stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data":{"currency":"usd","product_data":{"name":f"Advisory Ref: {awb}"},"unit_amount":int(amount*100)},"quantity":1}],
            mode="payment",
            success_url=f"{domain}/?access=granted&awb={urllib.parse.quote(awb)}&monto={amount}",
            cancel_url=f"{domain}/"
        )
        return {"url":checkout.url}
    except Exception as e: return JSONResponse({"error":str(e)},status_code=400)
