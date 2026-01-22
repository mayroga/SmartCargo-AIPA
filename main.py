import os, httpx
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configuración de Identidad y Reglas de Respuesta
TECH_CORE = """
Eres el CEREBRO ESTRATÉGICO de SMARTCARGO ADVISORY by MAY ROGA LLC. 
IDENTIDAD: Consultor logístico privado de alto nivel. No eres gobierno, IATA, TSA ni DOT.
FILOSOFÍA: Mitigar retenciones, maximizar capital y prevenir errores operativos.

REGLAS CRÍTICAS DE RESPUESTA:
1. MEDIDAS DUALES: Siempre entrega dimensiones en [Pulgadas] INC y [Centímetros] CM.
2. SIN SÍMBOLOS: Prohibido usar asteriscos (*), hashtags (#) o Markdown complejo. La respuesta debe ser texto limpio para lectura de voz.
3. TONO: Profesional, decisivo y consultivo. No des órdenes, ofrece sugerencias y propuestas de acción.
4. RESOLUCIÓN: Si falta información, pregunta con precisión. Mantén el hilo hasta resolver el problema.
5. IDIOMA: Responde estrictamente en el idioma solicitado por el usuario.
"""

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.post("/advisory")
async def advisory_engine(
    prompt: str = Form(...), 
    history: Optional[str] = Form(""),
    lang: str = Form("es"), 
    role: Optional[str] = Form("auto")
):
    # Construcción del Prompt de Sistema
    system_instr = f"{TECH_CORE}\nIdioma: {lang}. Rol del Cliente: {role}.\nCONTEXTO PREVIO: {history}\nCONSULTA: {prompt}"
    
    async with httpx.AsyncClient(timeout=40.0) as client:
        # PLAN A: MOTOR PRINCIPAL (Velocidad Flash)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                res = await client.post(
                    url, 
                    json={"contents": [{"parts": [{"text": system_instr}]}]},
                    headers={"Content-Type": "application/json"}
                )
                if res.status_code == 200:
                    return {"data": res.json()["candidates"][0]["content"]["parts"][0]["text"]}
            except Exception as e:
                print(f"Error Motor 1: {e}")

        # PLAN B: MOTOR DE RESPALDO (Alta Complejidad)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": "gpt-4o",
                        "messages": [{"role": "system", "content": system_instr}],
                        "temperature": 0.3
                    }
                )
                if res.status_code == 200:
                    return {"data": res.json()["choices"][0]["message"]["content"]}
            except Exception as e:
                print(f"Error Motor 2: {e}")

    return {"data": "ERROR DE CONEXIÓN: El cerebro de asesoría no está disponible. Verifique su red."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
