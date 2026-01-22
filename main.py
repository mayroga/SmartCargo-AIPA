<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SmartCargo - Avianca Specialist</title>
    <style>
        :root { --avianca-red: #d32f2f; --gold: #c5a059; --dark: #0a192f; --light-bg: #f4f7f9; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { background: #000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; color: #fff; }
        
        .app { width: 100vw; min-height: 100vh; background: var(--dark); padding: 15px; display: flex; flex-direction: column; }
        
        /* Escudo Legal */
        .shield { background: var(--avianca-red); border: 2px solid #fff; padding: 12px; border-radius: 10px; font-size: 10px; font-weight: bold; text-align: center; margin-bottom: 15px; line-height: 1.2; }

        .card { background: #fff; border-radius: 20px; padding: 20px; color: #333; flex-grow: 1; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        /* Grid de Fotos */
        .photo-grid { display: grid; grid-template-columns: 1fr; gap: 15px; margin: 15px 0; }
        .photo-box { height: 250px; background: #f0f2f5; border: 3px dashed var(--gold); border-radius: 15px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; cursor: pointer; }
        .photo-box img { width: 100%; height: 100%; object-fit: contain; z-index: 2; }
        .photo-box span { position: absolute; font-size: 12px; font-weight: bold; color: var(--dark); text-align: center; padding: 10px; }

        /* Módulo de Rentabilidad (Volumen) */
        .profit-module { background: #fffbe6; border: 1px solid #ffe58f; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
        .profit-module strong { display: block; margin-bottom: 8px; font-size: 12px; color: #856404; text-transform: uppercase; }
        .dim-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
        
        .checklist { font-size: 11px; color: #555; margin: 15px 0; border: 1px solid #ddd; padding: 10px; border-radius: 8px; background: var(--light-bg); }
        
        .btn-exec { width: 100%; padding: 20px; background: var(--avianca-red); color: #fff; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; text-transform: uppercase; transition: 0.3s; }
        .btn-exec:active { transform: scale(0.98); }
        .btn-exec:disabled { background: #aaa; cursor: not-allowed; }

        input, textarea, select { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 10px; font-size: 14px; outline: none; }
        textarea { height: 80px; resize: none; }

        #resBox { display: none; margin-top: 20px; background: #eef2f7; padding: 15px; border-radius: 10px; border-left: 5px solid var(--gold); }
        .res-text { font-size: 14px; line-height: 1.5; color: var(--dark); white-space: pre-wrap; }
    </style>
</head>
<body>

<div class="app">
    <div class="shield">
        PRIVATE STRATEGIC ADVISORY BY MAY ROGA LLC. NOT A GOVERNMENT ENTITY. SPECIALIZED IN AVIANCA CARGO HUB STANDARDS.
    </div>

    <div class="card">
        <h2 style="margin:0; color:var(--dark); font-size: 18px;">Cargo Inspection Expert</h2>
        <p style="font-size: 11px; color: var(--gold); margin-bottom: 15px; font-weight: bold;">AVIANCA HUB PROTOCOL: ZERO REJECTIONS</p>

        <input type="text" id="awb" placeholder="AWB / Manifest Number">

        <div class="profit-module">
            <strong>💰 Profit Protection: Volume Check</strong>
            <div class="dim-grid">
                <input type="number" id="L" placeholder="L">
                <input type="number" id="W" placeholder="W">
                <input type="number" id="H" placeholder="H">
            </div>
            <div style="display:flex; gap:8px;">
                <input type="number" id="actW" placeholder="Actual Weight" style="flex:2;">
                <select id="unit" style="flex:1;">
                    <option value="CM">CM/KG</option>
                    <option value="INC">INC/LB</option>
                </select>
            </div>
            <button onclick="calcVol()" style="width:100%; background:var(--dark); color:#fff; border:none; padding:8px; border-radius:5px; font-size:10px; cursor:pointer;">VERIFY CHARGEABLE WEIGHT</button>
            <div id="vRes" style="font-size:11px; margin-top:5px; font-weight:bold; color:var(--avianca-red);"></div>
        </div>

        <div class="photo-grid">
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
        </div>

        <textarea id="obs" placeholder="Describe findings (e.g. PMC net tension, labeling, DG segregation)"></textarea>

        <button id="exec" class="btn-exec" onclick="process()">Execute Technical Advisory</button>

        <div id="resBox">
            <div id="resTxt" class="res-text"></div>
            <div style="display:flex; gap:10px; margin-top:15px;">
                <button onclick="window.print()" style="flex:1; padding:10px; border-radius:8px; background:#fff; border:1px solid #333;">PDF REPORT</button>
                <button onclick="speak()" style="flex:1; padding:10px; border-radius:8px; background:var(--dark); color:#fff; border:none;">🔊 LISTEN</button>
            </div>
        </div>
    </div>
</div>

<script>
    let volData = "";

    function calcVol() {
        const l = parseFloat(document.getElementById('L').value);
        const w = parseFloat(document.getElementById('W').value);
        const h = parseFloat(document.getElementById('H').value);
        const act = parseFloat(document.getElementById('actW').value);
        const unit = document.getElementById('unit').value;
        if(!l || !w || !h || !act) return alert("Complete dimensions");
        
        let vW = (unit === "CM") ? (l*w*h)/6000 : (l*w*h)/166;
        let chargeable = Math.max(act, vW);
        volData = `\n[Cubic Analysis] Chargeable: ${chargeable.toFixed(2)} vs Actual: ${act} ${unit}.`;
        document.getElementById('vRes').innerText = `CHARGEABLE: ${chargeable.toFixed(2)} ${unit}`;
    }

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
        btn.innerText = "VERIFYING AVIANCA STANDARDS...";
        box.style.display = "block";
        txt.innerText = "Analyzing documentation, cubic data, and cargo integrity...";

        const fd = new FormData();
        fd.append('prompt', document.getElementById('obs').value + volData);
        fd.append('role', 'Avianca Cargo Specialist');
        fd.append('awb', document.getElementById('awb').value);

        try {
            const res = await fetch('https://smartcargo-backend-production.up.railway.app/advisory', { method: 'POST', body: fd });
            const json = await res.json();
            txt.innerText = json.data;
        } catch (e) {
            txt.innerText = "Connection Error. Verify local HUB network.";
        } finally {
            btn.disabled = false;
            btn.innerText = "Execute Technical Advisory";
        }
    }

    function speak() {
        const ut = new SpeechSynthesisUtterance(document.getElementById('resTxt').innerText);
        window.speechSynthesis.speak(ut);
    }
</script>
</body>
</html>
