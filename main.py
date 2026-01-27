import os
import json
import requests
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import pytesseract
import tempfile

# =========================
# CONFIG
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "gemini-pro:generateContent"
)

HEADERS = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

# =========================
# FASTAPI
# =========================
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# OCR FUNCTION
# =========================
def run_ocr(image_file: UploadFile) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image_file.file.read())
            tmp_path = tmp.name

        image = Image.open(tmp_path)
        text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception as e:
        return f"OCR_ERROR: {str(e)}"


# =========================
# GEMINI CALL
# =========================
def call_gemini(prompt: str) -> str:
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(
            GEMINI_ENDPOINT,
            headers=HEADERS,
            data=json.dumps(payload),
            timeout=20
        )

        if response.status_code != 200:
            return f"GEMINI_ERROR: {response.text}"

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"GEMINI_EXCEPTION: {str(e)}"


# =========================
# VALIDATION ENDPOINT
# =========================
@app.post("/validate")
async def validate_cargo(
    mawb: str = Form(...),
    cargo_type: str = Form(...),
    image: UploadFile = None
):
    # 1️⃣ OCR
    ocr_text = ""
    if image:
        ocr_text = run_ocr(image)

    # 2️⃣ PROMPT MEJORADO (NO CAMBIA LÓGICA)
    prompt = f"""
YOU ARE A SENIOR AVIATION CARGO COUNTER INSPECTOR.

Analyze the cargo documentation and situation exactly as a real counter would.

Rules:
- ACCEPT → everything correct
- CONDITIONAL → minor discrepancies but correctable
- REJECT → safety, legal, or documentation violation

Return ONLY:
STATUS: ACCEPT / CONDITIONAL / REJECT
REASONS: bullet list

DATA:
MAWB: {mawb}
CARGO TYPE: {cargo_type}

OCR TEXT:
{ocr_text}
"""

    # 3️⃣ GEMINI
    gemini_result = call_gemini(prompt)

    # 4️⃣ FALLBACK SI GEMINI FALLA
    if gemini_result.startswith("GEMINI_"):
        return JSONResponse({
            "status": "CONDITIONAL",
            "source": "SYSTEM_FALLBACK",
            "reason": "AI unavailable, manual review required",
            "ocr": ocr_text
        })

    return JSONResponse({
        "status": "OK",
        "source": "GEMINI",
        "analysis": gemini_result,
        "ocr": ocr_text
    })


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"system": "SmartCargo-AIPA", "status": "RUNNING"}
