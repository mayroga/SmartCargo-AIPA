import os, stripe, httpx, base64, io, re, openai
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from dotenv import load_dotenv

from google import genai
from google.genai import types
from PIL import Image, ImageOps

# =====================================================
# ENV
# =====================================================
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not GEMINI_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")

_gemini = genai.Client(api_key=GEMINI_KEY)

# =====================================================
# FASTAPI
# =====================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =====================================================
# VISUAL ADVISOR CORE (MOBILE SAFE – REAL VISION)
# =====================================================
def describe_image(image_bytes: bytes) -> str:
    try:
        # --- NORMALIZAR IMAGEN DE CELULAR ---
        img = Image.open(io.BytesIO(image_bytes))
        img.load()
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")

        if max(img.size) > 1600:
            img.thumbnail((1600, 1600))

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82, optimize=True)
        jpeg_bytes = buf.getvalue()

        if len(jpeg_bytes) < 1500:
            raise Exception("Invalid image")

        prompt = (
            "Analyze this image as a PRIVATE LOGISTICS VISUAL ADVISOR. "
            "Focus on the cargo itself. Detect real problems in loading, "
            "weight distribution, packaging, labeling, visible documents, "
            "or handling. Provide DIRECT, ACTIONABLE SOLUTIONS ONLY "
            "(move, adjust, secure, re-label, separate, redistribute). "
            "This is preventive technical advisory, not a legal or regulatory decision."
        )

        response = _gemini.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_text(prompt),
                types.Part.from_bytes(
                    data=jpeg_bytes,
                    mime_type="image/jpeg"
                )
            ]
        )

        if not response or not response.text:
            raise Exception("Empty response")

        return response.text.strip()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Visual advisory could not be generated"
        )

# =====================================================
# ROUTES
# =====================================================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/success")
async def success():
    return FileResponse("success.html")

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js")

# =====================================================
# MAIN ADVISORY ENDPOINT (TEXT + IMAGES)
# =====================================================
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...),
    lang: str = Form("en"),
    images: List[UploadFile] = File(None)
):
    reports = []

    # ---- VISUAL ANALYSIS FIRST ----
    if images:
        for img in images[:3]:
            raw = await img.read()
            vision = describe_image(raw)
            reports.append(vision)

    # ---- TEXT CONTEXT ----
    instruction = (
        f"You are the Senior Technical Advisor for SMARTCARGO by MAY ROGA LLC. "
        f"Answer in {lang}. "
        "MISSION: Solve real logistics problems fast. "
        "Provide ACTION PLANS, not theory. "
        "LEGAL SHIELD: PRIVATE ADVISORY ONLY. Not IATA, TSA, DOT, or any authority. "
        "Never mention AI."
    )

    combined_input = instruction + "\n\nCLIENT ISSUE:\n" + prompt
    if reports:
        combined_input += "\n\nVISUAL FINDINGS:\n" + "\n\n".join(reports)

    # ---- GEMINI TEXT REFINEMENT ----
    try:
        response = _gemini.models.generate_content(
            model="gemini-1.5-flash",
            contents=combined_input
        )
        if response and response.text:
            return {"data": response.text.strip()}
    except:
        pass

    # ---- BACKUP OPENAI ----
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": combined_input}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error: {str(e)}"}

    return {"data": "System busy. Try again later."}

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

# =====================================================
app.mount("/static", StaticFiles(directory="."), name="static")
