import os
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# REGLAS DE ORO: 2 SUGERENCIAS, BREVE, ASESORÍA
SYSTEM_ADVISOR = """
Eres un ASESOR TÉCNICO de carga aérea. 
REGLAS:
1. Solo da DOS (2) sugerencias técnicas por respuesta.
2. Sé breve y entendible.
3. Siempre usa tono de sugerencia ("Remediación recomendada").
4. No eres autoridad (TSA/IATA), solo asesoras para evitar rechazos.
"""

@app.post("/advisory")
async def advisory(prompt: str = Form(...), image: UploadFile = File(None)):
    try:
        contents = [prompt]
        if image:
            img_bytes = await image.read()
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=image.content_type))
        
        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_ADVISOR)
        )
        return {"data": res.text}
    except Exception as e:
        return {"data": "Error de conexión técnica."}
