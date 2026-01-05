from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import base64

# =====================================================
# CONFIGURACIÓN APP
# =====================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# CONFIGURACIÓN GEMINI (VISIÓN)
# =====================================================
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

VISION_MODEL = "gemini-1.5-flash"

# =====================================================
# FUNCIÓN VISUAL (NUNCA FALLA)
# =====================================================
def visual_advisory(image_bytes: bytes) -> str:
    try:
        encoded = base64.b64encode(image_bytes).decode("utf-8")

        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": encoded
                            }
                        },
                        {
                            "text": (
                                "You are SMARTCARGO by May Roga LLC. "
                                "Provide a DIRECT, TECHNICAL, ACTIONABLE visual advisory. "
                                "Focus on cargo condition, positioning, weight distribution, "
                                "packaging integrity, labeling, safety, and transport compliance. "
                                "Give solutions, not warnings."
                            )
                        }
                    ]
                }
            ]
        )

        return response.text.strip()

    except Exception:
        # FALLBACK ABSOLUTO → NUNCA DEVUELVE NONE
        return (
            "Visual evidence received. Unable to generate full visual advisory. "
            "Verify cargo stability, weight distribution, package integrity, "
            "and required labels before transport."
        )

# =====================================================
# ENDPOINT PRINCIPAL
# =====================================================
@app.post("/advisory")
async def advisory(
    files: list[UploadFile] = File(None),
    prompt: str = Form(""),
    lang: str = Form("en")
):
    reports = []

    # ---- PROCESAR IMÁGENES ----
    if files:
        for f in files[:3]:
            try:
                img_bytes = await f.read()
                report = visual_advisory(img_bytes)
                reports.append(report)
            except Exception:
                reports.append(
                    "Image received. Manual inspection recommended for cargo positioning and safety."
                )

    # ---- CONTEXTO USUARIO ----
    if prompt.strip():
        reports.append(f"User context: {prompt.strip()}")

    # ---- RESPUESTA FINAL (NUNCA VACÍA) ----
    final_report = "\n\n".join(reports).strip()

    if not final_report:
        final_report = (
            "No visual or contextual data detected. "
            "Ensure cargo is properly secured, labeled, and compliant before delivery."
        )

    return JSONResponse({"data": final_report})


# =====================================================
# HEALTH CHECK
# =====================================================
@app.get("/")
def root():
    return {"status": "SMARTCARGO ONLINE"}
