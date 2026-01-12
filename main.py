import os, httpx, urllib.parse
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="SmartCargo Advisory by May Roga LLC")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/app.js")
async def js_serve(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("es"), role: Optional[str] = Form("auto")):
    
    # KNOWLEDGE INJECTION: IATA, TSA, DOT, CBP, AVIANCA STANDARDS
    system_instruction = f"""
    YOU ARE THE STRATEGIC ADVISORY BRAIN OF SMARTCARGO ADVISORY BY MAY ROGA LLC.
    MISSION: Educate, Prevent, and Mitigate errors BEFORE, DURING, and AFTER counter delivery.
    
    TECHNICAL MANDATES:
    1. PAPERWORK: Verify AWB Originals 2 & 4. Manifests must be legible. Keep papers OUTSIDE the envelope to avoid 'Human Mixing Errors'.
    2. CARGO: 96" max length for Avianca. Bellies (PAX) max height 63". DG labels MUST face OUTWARD for inspectors.
    3. STANDARDS: ISPM-15 seals for wood pallets. No black tape. No moisture.
    4. ROLES: 
       - SHIPPER: UN packaging, marks, and labels.
       - FORWARDER: Exact text for AWB and DGD.
       - TRUCKER: DOT standards, load securing, BOL awareness.
       - COUNTER/STAFF: CAO check (>160cm), weight discrepancies, security seals.
    
    RESPONSE STRUCTURE:
    - [OPERATIONAL ADVICE] Strategic path to follow.
    - [TECHNICAL DIAGNOSIS] Error identification and immediate solution.
    - [CALCULATION] Volumetric weight (L x W x H cm / 6000).
    - [WHY] Fines prevention (TSA/CBP) and avoiding Avianca rejections.
    
    Language: {lang}. User Role: {role}. INPUT: {prompt}
    """

    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            async with httpx.AsyncClient(timeout=45.0) as client:
                payload = {"contents": [{"parts": [{"text": system_instruction}]}], "generationConfig": {"temperature": 0.1}}
                r = await client.post(url, json=payload)
                if r.status_code == 200:
                    return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception: pass

    return {"data": "System processing technical load. Please retry."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    # Simple login logic for Master Access
    if user == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
        return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}"}
    return {"url": f"/?access=granted&awb={urllib.parse.quote(awb)}"}
