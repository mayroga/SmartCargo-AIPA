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
You are 'SmartCargo-AIPA', the supreme AI specialist for Avianca Cargo. 
You master IATA DGR, LAR, PCR, DOT Title 49, and CBP/TSA security.

YOUR RESPONSIBILITIES:
1. SHIPPER/OWNER: Advise on packaging and required docs.
2. WAREHOUSE OPS: PMC/AKE buildup, net tension, and floor limits.
3. PROFIT PROTECTION: You must analyze the volume provided. If the Volumetric Weight is higher than Actual Weight, advise the user to charge based on Volume.

LEGAL: Use advisory language. NEVER use 'audit', 'AI', or 'Government'.
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>SmartCargo-AIPA | Avianca HUB</title>
        <style>
            :root { --red: #d32f2f; --gold: #c5a059; --dark: #0a192f; --white: #ffffff; }
            * { box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
            body { background: #000; margin: 0; color: var(--white); }
            .container { width: 100vw; min-height: 100vh; background: var(--dark); padding: 15px; }
            .header { text-align: center; border-bottom: 2px solid var(--gold); padding-bottom: 10px; position: relative; }
            .lang-btn { position: absolute; right: 0; top: 5px; background: var(--gold); border: none; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
            .shield { background: var(--red); color: white; padding: 8px; font-size: 10px; text-align: center; margin: 10px 0; border-radius: 5px; border: 1px solid white; }
            .main-card { background: var(--white); border-radius: 20px; padding: 20px; color: #333; }
            .photo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
            .photo-box { height: 100px; background: #f0f2f5; border: 2px dashed var(--gold); border-radius: 12px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
            .photo-box img { width: 100%; height: 100%; object-fit: contain; z-index: 2; }
            .calc-section { background: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
            .calc-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
            input, textarea { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 8px; font-size: 14px; }
            .btn-main { width: 100%; padding: 15px; background: var(--red); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
            #resBox { display: none; margin-top: 15px; background: #eef2f7; border-left: 6px solid var(--gold); padding: 15px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <button class="lang-btn" onclick="toggleLang()">ESPAÑOL</button>
                <h1 style="margin:0; font-size: 20px;">SmartCargo-AIPA</h1>
            </div>
            <div class="shield">PRIVATE STRATEGIC ADVISORY | AVIANCA LOGISTICS BRAIN</div>
            
            <div class="main-card">
                <input type="text" id="awb" placeholder="AWB / ULD NUMBER">
                
                <div class="calc-section">
                    <strong id="volTitle">Profit & Volume Calculator</strong>
                    <div class="calc-grid" style="margin-top:10px;">
                        <input type="number" id="L" placeholder="L">
                        <input type="number" id="W" placeholder="W">
                        <input type="number" id="H" placeholder="H">
                    </div>
                    <div class="calc-grid">
                        <input type="number" id="pcs" placeholder="PCS">
                        <input type="number" id="weight" placeholder="Actual Weight">
                        <select id="unit" style="padding:10px; border-radius:8px; border:1px solid #ccc;">
                            <option value="INC">INC/LB</option>
                            <option value="CM">CM/KG</option>
                        </select>
                    </div>
                </div>

                <div class="photo-grid">
                    <div class="photo-box" onclick="document.getElementById('f1').click()">
                        <img id="v1" style="display:none;"><span id="t1">📸 DOCS</span>
                        <input type="file" id="f1" hidden onchange="pv(event,'v1')">
                    </div>
                    <div class="photo-box" onclick="document.getElementById('f2').click()">
                        <img id="v2" style="display:none;"><span id="t2">📸 CARGO</span>
                        <input type="file" id="f2" hidden onchange="pv(event,'v2')">
                    </div>
                </div>

                <textarea id="obs" placeholder="Describe findings..."></textarea>
                <button class="btn-main" onclick="runAIPA()" id="exec">EXECUTE TECHNICAL SOLUTION</button>

                <div id="resBox">
                    <div id="resTxt" style="color:#000; font-size:14px;"></div>
                    <button class="btn-main" style="background:var(--dark); margin-top:10px;" onclick="speak()">🔊 LISTEN</button>
                    <button class="btn-main" style="background:#fff; color:#333; border:1px solid #333; margin-top:5px;" onclick="window.print()">PRINT REPORT</button>
                </div>
            </div>
        </div>

        <script>
            let lang = 'EN';
            function toggleLang() {
                lang = lang === 'EN' ? 'ES' : 'EN';
                document.getElementById('volTitle').innerText = lang === 'EN' ? 'Profit & Volume Calculator' : 'Calculadora de Profit y Volumen';
                document.getElementById('exec').innerText = lang === 'EN' ? 'EXECUTE TECHNICAL SOLUTION' : 'OBTENER SOLUCIÓN TÉCNICA';
            }

            function pv(e, id) {
                const r = new FileReader();
                r.onload = x => { const i = document.getElementById(id); i.src = x.target.result; i.style.display = "block"; i.nextElementSibling.style.display="none"; };
                r.readAsDataURL(e.target.files[0]);
            }

            async function runAIPA() {
                const l = document.getElementById('L').value;
                const w = document.getElementById('W').value;
                const h = document.getElementById('H').value;
                const p = document.getElementById('pcs').value;
                const awb = document.getElementById('awb').value;
                const unit = document.getElementById('unit').value;
                const weight = document.getElementById('weight').value;

                let volMsg = `Dimensions: ${l}x${w}x${h} ${unit} | PCS: ${p} | Weight: ${weight}. `;
                
                const fd = new FormData();
                fd.append('prompt', volMsg + document.getElementById('obs').value);
                fd.append('awb', awb);
                fd.append('lang', lang);

                document.getElementById('resBox').style.display = "block";
                document.getElementById('resTxt').innerText = "Analyzing Profit & Standards...";

                const res = await fetch('/advisory', { method: 'POST', body: fd });
                const json = await res.json();
                document.getElementById('resTxt').innerText = json.data;
            }

            function speak() {
                const u = new SpeechSynthesisUtterance(document.getElementById('resTxt').innerText);
                u.lang = lang === 'EN' ? 'en-US' : 'es-ES';
                window.speechSynthesis.speak(u);
            }
        </script>
    </body>
    </html>
    """

@app.post("/advisory")
async def process_advisory(prompt: str = Form(...), awb: str = Form(...), lang: str = Form(...)):
    context = f"{SYSTEM_PROMPT}\nLanguage: {lang}\nAWB: {awb}\nReport: {prompt}\nTechnical Solution:"
    response = model.generate_content(context)
    return {"data": response.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
