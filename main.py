from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI(title="SmartCargo AIPA by MAY ROGA LLC")

# 1. SEGURIDAD DE CONEXIÓN (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. CONFIGURACIÓN DEL CEREBRO (GOOGLE GEMINI)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. INTERFAZ VISUAL INTEGRADA (HTML/CSS/JS)
# Se sirve en la raíz "/" para evitar el error "Not Found"
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>SmartCargo - Avianca Hub Specialist</title>
        <style>
            :root { --avianca-red: #d32f2f; --gold: #c5a059; --dark: #0a192f; }
            body { background: #000; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; color: #fff; }
            .app { width: 100vw; min-height: 100vh; background: var(--dark); padding: 15px; display: flex; flex-direction: column; }
            .shield { background: var(--avianca-red); border: 2px solid #fff; padding: 10px; border-radius: 8px; font-size: 10px; font-weight: bold; text-align: center; margin-bottom: 15px; }
            .card { background: #fff; border-radius: 20px; padding: 20px; color: #333; flex-grow: 1; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            .photo-box { height: 260px; background: #f0f2f5; border: 3px dashed var(--gold); border-radius: 15px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; margin-bottom: 15px; }
            .photo-box img { width: 100%; height: 100%; object-fit: contain; }
            .photo-box span { position: absolute; font-size: 12px; font-weight: bold; color: var(--dark); background: rgba(255,255,255,0.7); padding: 8px; border-radius: 5px; }
            .btn-exec { width: 100%; padding: 20px; background: var(--avianca-red); color: #fff; border: none; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
            .btn-exec:disabled { background: #ccc; }
            input, textarea { width: 100%; padding: 15px; border-radius: 10px; border: 1px solid #ccc; margin-bottom: 10px; font-size: 16px; box-sizing: border-box; }
            #resBox { display: none; margin-top: 20px; background: #eef2f7; padding: 15px; border-radius: 10px; border-left: 5px solid var(--gold); }
        </style>
    </head>
    <body>
        <div class="app">
            <div class="shield">PRIVATE STRATEGIC ADVISORY BY MAY ROGA LLC. NOT A GOVERNMENT ENTITY. SPECIALIZED IN AVIANCA CARGO STANDARDS.</div>
            <div class="card">
                <h2 style="margin:0; color:var(--dark);">Cargo Inspection Expert</h2>
                <p style="font-size: 12px; color: var(--gold); margin-bottom: 15px;">Target: Zero Rejections / Max Profit</p>
                
                <input type="text" id="awb" placeholder="AWB / Manifest Number">
                
                <div class="photo-box" onclick="document.getElementById('f1').click()">
                    <img id="v1" style="display:none;">
                    <span>📸 SCAN DOCUMENTS (AWB/DGD/SLI)</span>
                    <input type="file" id="f1" hidden onchange="pv(event,'v1')">
                </div>
                
                <div class="photo-box" onclick="document.getElementById('f2').click()">
                    <img id="v2" style="display:none;">
                    <span>📸 INSPECT PMC / CARGO INTEGRITY</span>
                    <input type="file" id="f2" hidden onchange="pv(event,'v2')">
                </div>

                <textarea id="obs" placeholder="Describe findings (e.g. damaged PMC base, illegible labels, segregation issues)"></textarea>
                
                <button id="exec" class="btn-exec" onclick="process()">Execute Technical Advisory</button>

                <div id="resBox">
                    <div id="resTxt" style="font-size: 14px; color:#0a192f; white-space:pre-wrap;"></div>
                    <button onclick="window.print()" style="margin-top:10px; width:100%; padding:10px; border-radius:8px; background:#fff; border:1px solid #333;">Generate PDF Report</button>
                </div>
            </div>
        </div>

        <script>
            function pv(e, id) {
                const r = new FileReader();
                r.onload = x => {
                    const i = document.getElementById(id);
                    i.src = x.target.result;
                    i.style.display = "block";
                    i.nextElementSibling.style.display = "none";
                };
                r.readAsDataURL(e.target.files[0]);
            }

            async function process() {
                const btn = document.getElementById('exec');
                const txt = document.getElementById('resTxt');
                const box = document.getElementById('resBox');
                if(!document.getElementById('awb').value) return alert("Enter AWB Number");

                btn.disabled = true;
                btn.innerText = "VERIFYING STANDARDS...";
                box.style.display = "block";
                txt.innerText = "Analyzing Documentation and Cargo Integrity...";

                const fd = new FormData();
                fd.append('prompt', document.getElementById('obs').value);
                fd.append('role', 'Avianca Specialist');
                fd.append('awb', document.getElementById('awb').value);

                try {
                    // LLAMA A LA RUTA /advisory DEL MISMO SERVIDOR
                    const res = await fetch('/advisory', { method: 'POST', body: fd });
                    const json = await res.json();
                    txt.innerText = json.data;
                } catch (e) {
                    txt.innerText = "Connection lost. Please retry.";
                } finally {
                    btn.disabled = false;
                    btn.innerText = "Execute Technical Advisory";
                }
            }
        </script>
    </body>
    </html>
    """

# 4. LÓGICA DEL CEREBRO ESPECIALISTA
SYSTEM_SPECIALIST = """
You are the Lead Logistics Advisor for 'SmartCargo Advisory by MAY ROGA LLC'.
Specialized in AVIANCA HUB operations.
- Measurements: Always [Inches] INC and [Centimeters] CM.
- Legal: NEVER use 'audit', 'AI', 'Intelligence', or 'Government'.
- Focus: ULD/PMC integrity, AWB legibility, 3 originals/6 copies rule, IATA DGR Table 9.3.A.
- Tone: Professional advisor ('It is suggested', 'Recommended action').
"""

@app.post("/advisory")
async def get_advisory(
    prompt: str = Form(...),
    role: str = Form(...),
    awb: str = Form(...),
):
    try:
        context = f"{SYSTEM_SPECIALIST}\nAWB: {awb}\nRole: {role}\nObservations: {prompt}\nSolution:"
        response = model.generate_content(context)
        return {"data": response.text}
    except Exception as e:
        return {"data": "Technical Hub recalibrating. Please wait."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
