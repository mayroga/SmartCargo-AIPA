import os
import io
import base64
import stripe
import httpx
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from dotenv import load_dotenv
from PIL import Image, ImageOps

# =====================================================
# INIT
# =====================================================
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

# =====================================================
# HEALTH + STATIC
# =====================================================
@app.get("/")
async def home():
    return {"status": "SMARTCARGO ONLINE"}

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js")

# =====================================================
# IMAGE NORMALIZER (CRÍTICO)
# =====================================================
def normalize_image(raw: bytes) -> bytes:
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")

    if img.width > 1600 or img.height > 1600:
        img.thumbnail((1600, 1600))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    data = buf.getvalue()

    if len(data) < 1500:
        raise ValueError("Image too small")

    return data

# =====================================================
# ADVISORY ENGINE
# =====================================================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    instruction = (
        "You are SMARTCARGO by MAY ROGA LLC.\n"
        "ROLE: PRIVATE VISUAL TECHNICAL ADVISOR (NOT AUTHORITY).\n"
        "MISSION: Prevent cargo rejection, fines, delays.\n\n"
        "RULES:\n"
        "- Analyze cargo as if it will be presented at a counter.\n"
        "- Decide if it is ACCEPTABLE or AT RISK.\n"
        "- Give DIRECT PHYSICAL ACTIONS.\n"
        "- Never be generic.\n"
        "- Never say ask someone else.\n"
        "- Never mention AI.\n\n"
        "FORMAT:\n"
        "VISUAL STATUS:\n"
        "WHY:\n"
        "WHAT TO DO NOW:\n"
        "COUNTER READINESS:\n\n"
        f"Language: {lang}"
    )

    parts = [{"text": f"{instruction}\n\nClient context:\n{prompt}"}]

    if files:
        for f in files[:3]:
            try:
                raw = await f.read()
                img_bytes = normalize_image(raw)
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_bytes).decode("utf-8")
                    }
                })
            except Exception:
                parts.append({
                    "text": (
                        "IMAGE ISSUE DETECTED:\n"
                        "Image could not be safely analyzed. "
                        "Ensure cargo is fully visible, well-lit, no blur."
                    )
                })

    if GEMINI_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            )
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url,
                    json={"contents": [{"parts": parts}]},
                    timeout=45.0
                )
                data = r.json()
                if "candidates" in data:
                    return JSONResponse({
                        "data": data["candidates"][0]["content"]["parts"][0]["text"]
                    })
        except Exception as e:
            print("Gemini error:", e)

    return JSONResponse({
        "data": (
            "Visual advisory could not be generated at this time.\n"
            "Ensure at least one clear image of the cargo is provided."
        )
    })

# =====================================================
# PAYMENT
# =====================================================
@app.post("/create-payment")
async def create_payment(
    amount: float = Form(...),
    awb: str = Form(...),
    user: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    base_url = "https://smartcargo-aipa.onrender.com"
    success_url = f"{base_url}/?access=granted&awb={awb}"

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
        cancel_url=base_url
    )
    return {"url": session.url}
