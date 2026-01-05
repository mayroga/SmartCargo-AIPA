import os
import io
import base64
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps
from google import genai

# =====================================================
# CONFIG
# =====================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing API key")

client = genai.Client(api_key=API_KEY)

# =====================================================
# ROOT HEALTH
# =====================================================
@app.get("/")
def root():
    return {"status": "SMARTCARGO ONLINE"}

# =====================================================
# IMAGE NORMALIZER (MOBILE SAFE)
# =====================================================
def normalize_image(raw: bytes) -> bytes:
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img.thumbnail((1600, 1600))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue()

# =====================================================
# GEMINI VISUAL ADVISORY
# =====================================================
def visual_advisory(image_bytes: bytes) -> str:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{
            "role": "user",
            "parts": [
                {
                    "text": (
                        "You are SMARTCARGO by May Roga LLC, a PROFESSIONAL VISUAL TECHNICAL ADVISOR.\n"
                        "Assume this cargo is about to be presented at an airport counter.\n\n"
                        "RULES:\n"
                        "- Analyze the image as REAL cargo.\n"
                        "- Decide if it is ACCEPTABLE or AT RISK.\n"
                        "- Give DIRECT physical actions.\n"
                        "- Do NOT give generic advice.\n"
                        "- Do NOT tell the user to ask others.\n\n"
                        "FORMAT:\n"
                        "1. VISUAL STATUS\n"
                        "2. WHY\n"
                        "3. WHAT TO DO NOW\n"
                        "4. FINAL COUNTER READINESS\n"
                    )
                },
                {
                    "inline_data": {
                        "data": image_bytes,
                        "mime_type": "image/jpeg"
                    }
                }
            ]
        }]
    )

    return response.text.strip() if response and response.text else (
        "Visual data received but no actionable advisory could be generated."
    )

# =====================================================
# MAIN ADVISORY ENDPOINT
# =====================================================
@app.post("/advisory")
async def advisory(
    files: list[UploadFile] = File(None),
    prompt: str = Form(""),
    lang: str = Form("en")
):
    reports = []

    if files:
        for f in files[:3]:
            raw = await f.read()
            try:
                img_bytes = normalize_image(raw)
                reports.append(visual_advisory(img_bytes))
            except Exception:
                reports.append(
                    "Image received but could not be safely analyzed. "
                    "Ensure the box is clearly visible, well-lit, and fully framed."
                )

    final_report = "\n\n".join(reports)

    if prompt.strip():
        final_report += f"\n\nUser context:\n{prompt}"

    if not final_report.strip():
        final_report = (
            "No visual evidence received. "
            "Upload at least one clear image of the cargo."
        )

    return JSONResponse({"data": final_report})
