import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- ENV ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- FILE SERVER ---
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

# --- ADVISORY ENGINE ---
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    images: List[UploadFile] = File(None)
):

    instruction = (
        f"You are SMARTCARGO CONSULTING, a private technical advisor. Answer in {lang}. "
        "You are NOT a government authority, NOT IATA, NOT TSA, NOT DOT, NOT DG certified. "
        "You do NOT touch, handle, approve, or transport cargo. This is advisory only.\n\n"

        "VISION RULE:\n"
        "When images are provided, they are the PRIMARY source of truth.\n"
        "You MUST visually inspect them before considering any text.\n"
        "Detect visible issues in packaging, labels, markings, AWB, delivery orders, or documents.\n\n"

        "OUTPUT RULES:\n"
        "- Give a PRACTICAL ACTION PLAN.\n"
        "- Use direct steps: Do this, Fix this, Replace this, Re-label this.\n"
        "- No legal lectures.\n\n"

        "ORDER:\n"
        "1) Fastest & cheapest fix.\n"
        "2) Intermediate solution.\n"
        "3) Structural improvement.\n\n"

        "Goal: cargo passes inspection on first attempt. Never mention AI."
    )

    # ---------- GEMINI (PRIMARY, VISUAL-FIRST) ----------
    if GEMINI_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            )

            parts = []

            # 1️⃣ IMAGES FIRST (PRIMARY SOURCE)
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

            # 2️⃣ TEXT SECONDARY
            parts.append({
                "text": (
                    instruction +
                    "\n\nIMPORTANT:\n"
                    "The images above are the PRIMARY source of truth.\n"
                    "Inspect them carefully before using the text below.\n\n"
                    f"Client description (secondary):\n{prompt}"
                )
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

    # ---------- OPENAI BACKUP ----------
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

# --- PAYMENTS ---
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
