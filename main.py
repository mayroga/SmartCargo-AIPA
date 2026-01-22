import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI(title="SmartCargo-AIPA by MAY ROGA LLC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """
You are 'SmartCargo-AIPA', the Lead Operations Advisor for Avianca Cargo.
KNOWLEDGE BASE:
- Avianca Fleet: A330F (High capacity, nose loading) & 767-300F.
- ULD Selection: PMC (Pallet) for oversized/general, AKE (Container) for loose/security.
- Priorities: Must-Go (Perishables/VAL), General Cargo, Stand-by.
- Fuel Saving: Advise on ULD positioning (Aft/Forward) to optimize Center of Gravity (CoG).
- Compliance: IATA DGR, DOT, CBP.

OPERATIONAL MANDATE:
- Calculations: Use 1:6 volumetric ratio. 
- Dimensions: Handle INC and CM. Weight: Handle LB and KG.
- Logic: If volume exceeds PMC limits, suggest A330F. If cargo is DG, apply segregation.
- Tone: Professional, Advisory. Never say 'AI' or 'Government'.
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/advisory")
async def process_advisory(
    prompt: str = Form(...), 
    awb: str = Form(...), 
    lang: str = Form(...),
    l: str = Form(None), w: str = Form(None), h: str = Form(None),
    pcs: str = Form(None), wgt: str = Form(None), unit: str = Form(None)
):
    # Construcción de la data técnica para la IA
    tech_data = f"""
    --- CARGO TECHNICAL DATA ---
    AWB/ULD: {awb}
    Dimensions: {l}x{w}x{h} {unit}
    Pieces: {pcs} | Actual Weight: {wgt}
    User Observations: {prompt}
    ----------------------------
    """
    
    context = f"{SYSTEM_PROMPT}\nRespond in {lang}.\n{tech_data}\n" \
              "PROVIDE: 1. ULD Suggestion. 2. Aircraft Recommendation. 3. Shipment Priority. " \
              "4. Fuel Saving Position (CoG). 5. Documentation Review."
    
    try:
        response = model.generate_content(context)
        return {"data": response.text}
    except Exception as e:
        return {"data": "System busy. Confirm PMC/AKE integrity manually."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
