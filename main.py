import os, stripe, httpx, base64, openai
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Blindaje de seguridad para que el navegador permita todas las funciones
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- VARIABLES DE ENTORNO (Render) ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- SERVIDOR DE ARCHIVOS ---
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

# --- MOTOR ASESOR (Gemini + OpenAI Backup) ---
@app.post("/advisory")
async def advisory_engine(
    action: str = Form(...),  # 'inspection' o 'consulta'
    prompt: str = Form(""),
    lang: str = Form("en"),
    files: List[UploadFile] = File(None)
):
    # --- Instrucciones base ---
    base_instruction = (
        f"You are SMARTCARGO CONSULTING. Answer in {lang}. "
        "You are a private logistics consultant. Give actionable, practical solutions. "
        "Do NOT give legal verdicts. Prioritize satisfaction and fast, palpable results. "
        "Do not mention AI. Focus on the action the client wants to take."
    )

    # --- Acción de INSPECCIÓN: Fotos y documentos primero ---
    if action == "inspection":
        if not files or len(files) == 0:
            return {"data": "Please upload at least one photo or document for inspection."}

        instruction = (
            base_instruction +
            "\nPRIORITY: Analyze uploaded images and documents first. "
            "Give a tactical 'Action Plan' so cargo passes inspections or processes correctly. "
            "Only after inspecting files, you may ask for textual input if needed."
        )

        parts = [{"text": instruction + "\n\nInspect the following client files:"}]
        for f in files[:5]:  # máximo 5 archivos
            content = await f.read()
            if content:
                parts.append({"inline_data": {"mime_type": f.content_type, "data": base64.b64encode(content).decode("utf-8")}})

        if GEMINI_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                async with httpx.AsyncClient() as client:
                    r = await client.post(url, json={"contents": [{"parts": parts}]}, timeout=60.0)
                    return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
            except: pass

        if OPENAI_KEY:
            try:
                client = openai.OpenAI(api_key=OPENAI_KEY)
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": instruction}]
                )
                return {"data": res.choices[0].message.content}
            except Exception as e:
                return {"data": f"Error: {str(e)}"}

        return {"data": "System busy. Try again later."}

    # --- Acción de CONSULTA TEXTO ---
    elif action == "consulta":
        if not prompt:
            return {"data": "Please write your question or describe your problem."}

        instruction = (
            base_instruction +
            "\nCLIENT REQUEST: " + prompt
        )

        if GEMINI_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                async with httpx.AsyncClient() as client:
                    r = await client.post(url, json={"contents": [{"parts": [{"text": instruction}]}]}, timeout=45.0)
                    return {"data": r.json()["candidates"][0]["content"]["parts"][0]["text"]}
            except: pass

        if OPENAI_KEY:
            try:
                client = openai.OpenAI(api_key=OPENAI_KEY)
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
                )
                return {"data": res.choices[0].message.content}
            except Exception as e:
                return {"data": f"Error: {str(e)}"}

        return {"data": "System busy. Try again later."}

    else:
        return {"data": "Invalid action. Choose 'inspection' or 'consulta'."}

# --- PAGOS Y ACTIVACIÓN ---
@app.post("/create-payment")
async def create_payment(amount: float = Form(...), awb: str = Form(...), user: Optional[str] = Form(None), password: Optional[str] = Form(None)):
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
