import os
import stripe
import httpx
import openai
import urllib.parse
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

# =========================
# INIT
# =========================
load_dotenv()
app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# ENV VARS
# =========================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# =========================
# STATIC FILES
# =========================
@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/app.js")
async def js_serve():
    return FileResponse("app.js")

# =========================
# HELPER: Parse modern AI response
# =========================
def parse_ai_response(response_json):
    """Extrae todo el texto de candidatos/blocks/parts de Gemini o bloques de OpenAI."""
    text = ""
    # Gemini-style
    if "candidates" in response_json:
        for c in response_json["candidates"]:
            if "content" in c:
                parts = c["content"].get("parts", [])
                for p in parts:
                    if "text" in p:
                        text += p["text"] + "\n"
    # OpenAI-style
    elif "choices" in response_json:
        try:
            text += response_json["choices"][0]["message"]["content"]
        except:
            pass
    return text.strip()


# =========================
# CORE ADVISORY ENGINE
# =========================
@app.post("/advisory")
async def advisory_engine(
    prompt: Optional[str] = Form(None),  # opcional
    lang: str = Form("en"),
    image_data: Optional[str] = Form(None)
):
    instruction = (
        f"You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Language: {lang}. "
        "Provide EXECUTIVE SOLUTIONS only.\n\n"
        "STRUCTURE:\n"
        "1. DIRECT DIAGNOSIS\n"
        "2. WHERE TO LOOK\n"
        "3. THREE ACTIONABLE SOLUTIONS\n\n"
        "RULES:\n"
        "- Be direct. No theory.\n"
        "- If image provided, analyze FIRST.\n"
        "- We are PRIVATE. NOT GOVERNMENT.\n\n"
        "--- SmartCargo Advisory by MAY ROGA LLC ---"
    )

    result = {"data": "SYSTEM: No data received.", "image": image_data}

    # limpiar Base64 si existe
    image_data_clean = None
    if image_data and "," in image_data:
        image_data_clean = image_data.split(",")[1].replace(" ", "+").strip()
    elif image_data:
        image_data_clean = image_data

    # =========================
    # PLAN A — GEMINI
    # =========================
    try:
        if GEMINI_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            parts = []
            if instruction:
                parts.append({"text": instruction})
            if prompt:
                parts.append({"text": prompt})
            if image_data_clean:
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data_clean}})

            async with httpx.AsyncClient(timeout=45.0) as client:
                r = await client.post(url, json={
                    "contents": [{"parts": parts}],
                    "generationConfig": {"maxOutputTokens": 600, "temperature": 0.1}
                })
                text = parse_ai_response(r.json())
                if text:
                    result["data"] = text
                    return result
    except Exception as e:
        print("Gemini Error:", e)

    # =========================
    # PLAN B — OPENAI BACKUP
    # =========================
    try:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            content = []
            if instruction:
                content.append({"type": "text", "text": instruction})
            if prompt:
                content.append({"type": "text", "text": prompt})
            # OpenAI solo acepta URL para imagen; si es Base64, se ignora
            if image_data_clean and image_data_clean.startswith("http"):
                content.append({"type": "image_url", "image_url": {"url": image_data_clean}})

            if content:
                res = client_oa.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=600
                )
                text = parse_ai_response(res.to_dict())
                if text:
                    result["data"] = text
    except Exception as e:
        result["data"] = f"TECH ERROR: {str(e)}"

    return result


# =========================
# VISION MICRO-SERVICE
# =========================
@app.post("/vision-scan")
async def vision_scan(
    image_data: str = Form(...),  # obligatorio
    lang: str = Form("en")
):
    prompt = (
        "Perform a strict visual inspection.\n"
        "If document: list visible fields, numbers, dates, signatures.\n"
        "If cargo: identify labels, UN numbers, damages, markings.\n"
        "Be objective. No assumptions."
    )

    image_data_clean = None
    # limpiar Base64 si viene en data URI
    if "," in image_data:
        image_data_clean = image_data.split(",")[1].replace(" ", "+").strip()
    else:
        image_data_clean = image_data

    result_text = None

    # =========================
    # PLAN A — GEMINI
    # =========================
    try:
        if GEMINI_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            parts = [{"text": prompt}]
            if image_data_clean:
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data_clean}})
            async with httpx.AsyncClient(timeout=45.0) as client:
                r = await client.post(url, json={
                    "contents": [{"parts": parts}],
                    "generationConfig": {"maxOutputTokens": 400, "temperature": 0.1}
                })
                result_text = parse_ai_response(r.json())
                if result_text:
                    return {"description": result_text}
    except Exception as e:
        print("Gemini Vision Error:", e)

    # =========================
    # PLAN B — OPENAI BACKUP
    # =========================
    try:
        if OPENAI_KEY:
            client_oa = openai.OpenAI(api_key=OPENAI_KEY)
            content = [{"type": "text", "text": prompt}]
            # solo si es URL, OpenAI puede analizar la imagen
            if image_data_clean and image_data_clean.startswith("http"):
                content.append({"type": "image_url", "image_url": {"url": image_data_clean}})
            res = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content}],
                max_tokens=400
            )
            result_text = parse_ai_response(res.to_dict())
            if result_text:
                return {"description": result_text}
    except Exception as e:
        return {"error": str(e)}

    return {"description": "SYSTEM: No data processed."}
