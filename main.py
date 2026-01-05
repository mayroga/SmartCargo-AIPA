import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv
# ===== SMARTCARGO IMAGE VISUAL ADVISOR — FINAL FIX =====
import os, base64, io, re
from fastapi import HTTPException
from google import genai
from google.genai import types
from PIL import Image, ImageOps

_API_KEY = os.getenv("GEMINI_API_KEY")
if not _API_KEY:
    raise RuntimeError("Server configuration error")

_client = genai.Client(api_key=_API_KEY)

def describe_image(image_b64: str) -> str:
    try:
        if not image_b64 or not isinstance(image_b64, str):
            raise Exception("Invalid input")

        # --- LIMPIEZA BASE64 ---
        image_b64 = re.sub(r"\s+", "", image_b64)
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]

        raw = base64.b64decode(image_b64, validate=False)

        # --- NORMALIZACIÓN MÓVIL ---
        img = Image.open(io.BytesIO(raw))
        img.load()
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")

        if max(img.size) > 1600:
            img.thumbnail((1600, 1600))

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82, optimize=True)
        img_bytes = buf.getvalue()

        if len(img_bytes) < 1500:
            raise Exception("Invalid image")

        # --- PROMPT SMARTCARGO ---
        prompt = (
            "Analiza esta imagen como un asesor visual profesional de logística. "
            "Detecta problemas reales en carga, estiba, embalaje, etiquetado, "
            "documentación visible o manipulación. "
            "Da soluciones claras y accionables para corregirlos y prevenir rechazos, "
            "daños o incumplimientos. "
            "La información es únicamente asesoría preventiva."
        )

        # 🔴 ESTA ES LA DIFERENCIA CRÍTICA 🔴
        response = _client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_text(prompt),
                types.Part.from_bytes(
                    data=img_bytes,
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
            detail="No se pudo generar la asesoría visual"
        )

# ======================================================


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

@app.get("/success")
async def success(): return FileResponse("success.html")

# Servir JS correctamente sin errores de ruta
@app.get("/app.js")
async def serve_js(): return FileResponse("app.js")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), lang: str = Form("en"), images: List[UploadFile] = File(None)):
    # INSTRUCCIÓN TÁCTICA ACTUALIZADA
    instruction = (
        f"You are the Senior Technical Advisor for SMARTCARGO by MAY ROGA LLC. Answer in {lang}. "
        "MISSION: Be a practical solver. Provide 'Action Plans' (Haz esto, acomoda aquello) to pass inspections immediately. "
        "LEGAL SHIELD: We are PRIVATE ADVISORS. Not IATA/TSA/DOT. Technical suggestions only, not a legal verdict. "
        "1. FASTEST SOLUTION. 2. INTERMEDIATE. 3. STRUCTURAL. Provide stability and hope. "
        "Identify risks with 🔴 [ALERT] or 🟢 [COMPLIANCE]. Never mention AI."
    )
   
    parts = [{"text": f"{instruction}\n\nClient Issue: {prompt}"}]
   
    # 1. Intentar con Gemini
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            if images:
                for img in images[:3]:
                    content = await img.read()
                    if content: parts.append({"inline_data": {"mime_type": img.content_type, "data": base64.b64encode(content).decode("utf-8")}})
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    # 2. Respaldo OpenAI (Opción B si falla Gemini)
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e: return {"data": f"Error: {str(e)}"}

    return {"data": "System busy. Try again later."}

@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    success_url = f"https://smartcargo-aipa.onrender.com/?access=granted&awb={awb}"
    if user == ADMIN_USER and password == ADMIN_PASS: return {"url": success_url}
   
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"Advisory AWB: {awb}"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
        mode="payment", success_url=success_url, cancel_url=success_url
    )
    return {"url": session.url}

app.mount("/static", StaticFiles(directory="."), name="static")                         
