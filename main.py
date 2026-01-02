import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv
from PIL import Image
import pytesseract  # OCR

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Variables de entorno
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- Servidor de archivos ---
@app.get("/")
async def home(): return FileResponse("index.html")

@app.get("/success")
async def success(): return FileResponse("success.html")

@app.get("/{file_name}.js")
async def serve_js(file_name: str):
    path = f"{file_name}.js"
    if os.path.exists(path): return FileResponse(path, media_type="application/javascript")
    return HTMLResponse("File not found", status_code=404)

# --- Motor Asesor ---
@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(None),
    lang: str = Form("en"),
    images: List[UploadFile] = File(None)
):
    # Instrucciones generales
    instruction = (
        f"You are SMARTCARGO CONSULTING. Answer in {lang}. "
        "You are a practical problem solver. "
        "Prioritize photos and documents for inspection. "
        "Give step-by-step actionable solutions so cargo passes inspection immediately. "
        "Never mention AI. This is advisory only, not a legal verdict."
    )

    ocr_texts = []

    # --- OCR de imágenes / documentos ---
    if images:
        for img_file in images[:3]:  # máximo 3 archivos
            try:
                content = await img_file.read()
                if not content:
                    continue
                image = Image.open(io.BytesIO(content))
                text = pytesseract.image_to_string(image, lang='eng')
                if text.strip():
                    ocr_texts.append(text.strip())
            except Exception as e:
                ocr_texts.append(f"[No se pudo leer la imagen {img_file.filename}]")

    # Si hay texto de imágenes, usamos eso como prompt prioritario
    final_prompt = ""
    if ocr_texts:
        final_prompt += "INSPECTION DATA FROM IMAGES/DOCS:\n" + "\n---\n".join(ocr_texts) + "\n\n"

    # Agregar prompt adicional del usuario si existe
    if prompt:
        final_prompt += f"ADDITIONAL USER QUESTION: {prompt}"

    if not final_prompt:
        return {"data": "No images or text provided for inspection."}

    # --- Intento 1: Gemini ---
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            parts = [{"text": f"{instruction}\n\n{final_prompt}"}]
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=45.0)
                return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
        except: pass

    # --- Intento 2: OpenAI ---
    if OPENAI_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_KEY)
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": final_prompt}]
            )
            return {"data": res.choices[0].message.content}
        except Exception as e:
            return {"data": f"Error: {str(e)}"}

    return {"data": "System busy. Try again later."}

# --- Pagos y Activación ---
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
