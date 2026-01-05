import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv
# ===== SMARTCARGO VISUAL ADVISORY — MOBILE SAFE & LEGAL =====
import os, base64, io
from fastapi import HTTPException
from google import genai
from PIL import Image, ImageOps

# --- API Key segura ---
_gk = os.getenv("GEMINI_API_KEY")
if not _gk:
    raise RuntimeError("Server config error")

_gc = genai.Client(api_key=_gk)

def describe_image(image_b64: str) -> str:
    """
    SMARTCARGO: convierte cualquier foto móvil y genera soluciones reales
    y legales para toda la cadena logística.
    Entradas: imagen base64 de celular.
    Salidas: asesoría paso a paso lista para que cada actor ejecute.
    """
    try:
        if not image_b64:
            raise Exception()

        # Quita prefijo base64 si existe
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]

        # Decodifica imagen
        raw = base64.b64decode(image_b64.strip(), validate=True)

        # ---- NORMALIZACIÓN DE IMÁGENES MÓVILES ----
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img) # Corrige orientación celular
        img = img.convert("RGB") # HEIC / RGBA / CMYK -> RGB
        img.thumbnail((1600, 1600)) # Tamaño seguro

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        img_bytes = buf.getvalue()
        if len(img_bytes) < 1024:
            raise Exception()

        # ---- PROMPT SMARTCARGO — SOLUCIONES REALES ----
        prompt = (
            "Actúa como un asesor visual experto en logística y transporte. "
            "Observa la imagen y proporciona soluciones prácticas, paso a paso, "
            "para toda la cadena: desde el dueño/shipper hasta operadores terrestres, "
            "marítimos y aéreos. "
            "Indica cómo mover, organizar, etiquetar o asegurar la carga, cómo verificar "
            "documentos, y cómo evitar riesgos legales u operativos. "
            "Genera instrucciones claras y accionables que resuelvan el problema, "
            "siempre legales y preventivas. "
            "Esta información es solo asesoría y debe ser validada por personal autorizado."
        )

        # ---- ENVÍO A GEMINI ----
        r = _gc.models.generate_content(
            model="gemini-1.5-flash",
            contents=[{
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"data": img_bytes, "mime_type": "image/jpeg"}}
                ]
            }]
        )

        # Validación de respuesta
        if not r or not r.candidates or not r.text:
            raise Exception()

        return r.text.strip()

    except Exception:
        raise HTTPException(500, "No se pudo procesar la imagen para asesoría SMARTCARGO")
# ==============================================
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
