import os, stripe, httpx, urllib.parse, base64, json
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

@app.post("/advisory")
async def advisory_engine(prompt: str = Form(...), image_data: Optional[str] = Form(None)):
    # 1. Instrucción Estricta (Formato System Prompt)
    instruction = "You are the Senior Master Advisor of SmartCargo (MAY ROGA LLC). Describe labels, UN codes, and hazards. Provide technical solutions. Finalize: '--- SmartCargo Advisory by MAY ROGA LLC. ---'"
    
    # 2. Construcción de Partes (Estructura Multimodal Estricta)
    payload_parts = [{"text": f"{instruction}\n\nUser Prompt: {prompt}"}]
    
    if image_data:
        try:
            # Limpieza Quirúrgica del Base64
            if "," in image_data:
                # Separar el encabezado y quedarse solo con los datos puros
                clean_base64 = image_data.split(",")[1].strip()
            else:
                clean_base64 = image_data.strip()
            
            payload_parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": clean_base64
                }
            })
        except Exception as e:
            return {"data": f"Error procesando lectura de imagen: {str(e)}"}

    # 3. Petición Directa a la API V1 (La más estable)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": payload_parts}]}

    async with httpx.AsyncClient() as client:
        try:
            # Timeout estricto de 20s para procesamiento visual
            response = await client.post(url, json=payload, headers=headers, timeout=20.0)
            response.raise_for_status() # Si no es 200, salta al error
            res_json = response.json()
            
            # Navegación profunda en el JSON para evitar 'NoneType'
            text_response = res_json['candidates'][0]['content']['parts'][0]['text']
            return {"data": text_response}
            
        except Exception as e:
            # Log de error crudo para diagnóstico en Render
            print(f"DEBUG_ERROR: {str(e)}")
            return {"data": f"Gemini API Error: {str(e)}"}

# Mantén tus rutas de / y /create-payment como estaban
