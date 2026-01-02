import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Blindaje CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- VARIABLES DE ENTORNO ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- ARCHIVOS ---
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/success")
async def success():
    return FileResponse("success.html")

@app.get("/{file_name}.js")
async def serve_js(file_name: str):
    path = f"{file_name}.js"
    if os.path.exists(path):
        return FileResponse(path, media_type="application/javascript")
    return HTMLResponse("File not found", status_code=404)

# --- MOTOR ASESOR ---
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    images: List[UploadFile] = File(None)
):
    instruction = (
    f"You are SMARTCARGO CONSULTING, a private technical advisor. Answer in {lang}. "
    "You are NOT a government authority, NOT IATA, NOT TSA, NOT DG certified. "
    "You do NOT handle or approve cargo. This is advisory, not a legal verdict.\n\n"

    "PRIORITY:\n"
    "- If photos are provided, analyze them FIRST and base conclusions on visual inspection.\n\n"

    "OUTPUT:\n"
    "- Give a PRACTICAL ACTION PLAN.\n"
    "- Use clear steps: Do this, Move this, Change packaging, Re-label.\n\n"

    "ORDER:\n"
    "1) Fastest & cheapest fix.\n"
    "2) Intermediate solution.\n"
    "3) Structural improvement.\n\n"

    "Goal: cargo passes inspection on first attempt. Never mention AI."
)

    # --- GEMINI (PRIORIDAD VISUAL) ---
    if GEMINI_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            )

            parts = [{"text": f"{instruction}\n\nClient Context:\n{prompt}"}]

            if images:
                for img in images[:3]:
                    content = await img.read()
                    if content:
                        parts.append({
                            "inline_data": {
                                "mime_type": img.content_type,
                                "data": base64.b64encode(content).decode("utf-8")
                            }
                        })

            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url,
                    json={"contents": [{"parts": parts}]},
                    timeout=45.0
                )

            return {
                "data": r.json()["candidates"][0]["content"]["parts"][0]["text"]
            }
        except:
            pass

    # --- OPENAI BACKUP ---
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error: {str(e)}"}

    return {"data": "System busy. Try again later."}

# --- PAGOS ---
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    success_url = f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}"

    if user == ADMIN_USER and password == ADMIN_PASS:
        return {"url": success_url}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Advisory AWB: {awb}"},
                "unit_amount": int(amount * 100)
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=success_url
    )

    return {"url": session.url}

app.mount("/static", StaticFiles(directory="."), name="static")
