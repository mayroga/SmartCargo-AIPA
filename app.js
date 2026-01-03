const content = {
    en: {
        promo: "<strong>Total Asset Protection.</strong> We ensure the <strong>Shipper's</strong> cargo reaches its destination safely, help <strong>Forwarders</strong> comply with TSA/Aeronautics, assist <strong>Truckers</strong> with DOT weight distribution, and eliminate 'Holds' at <strong>Warehouse</strong> entry for both commercial and passenger cargo.",
        t_pago: "1. PROTOCOL ACTIVATION",
        t_sol: "2. TECHNICAL SOLUTION CENTER",
        t_cam: "📷 CAPTURE VISUAL EVIDENCE",
        l_title: "⚠️ LEGAL DISCLAIMER - MAY ROGA LLC",
        l_desc: "Private advisory only. We are not a government agency (TSA/CBP). We do not certify Dangerous Goods. This analysis is based on international IATA/DOT/FMC standards to mitigate operational risk. Sessions are purged immediately after use."
    },
    es: {
        promo: "<strong>Protección Total.</strong> Aseguramos que la carga del <strong>Shipper</strong> llegue segura, ayudamos al <strong>Forwarder</strong> a cumplir con TSA/Aeronáutica, asistimos al <strong>Transportista</strong> con normas DOT de Florida y eliminamos 'Holds' en <strong>Bodega</strong> tanto para carga comercial como de pasajeros.",
        t_pago: "1. ACTIVACIÓN DE PROTOCOLO",
        t_sol: "2. CENTRO DE SOLUCIONES TÉCNICAS",
        t_cam: "📷 CARGAR EVIDENCIA VISUAL",
        l_title: "⚠️ AVISO LEGAL - MAY ROGA LLC",
        l_desc: "Asesoría privada únicamente. No somos agencia gubernamental (TSA/CBP). No certificamos Carga Peligrosa. Este análisis se basa en normas internacionales IATA/DOT/FMC para mitigar riesgos operativos. Las sesiones se purgan tras su uso."
    }
};

const technicalRoles = {
    shipper: "Export/Passenger Cargo Quality Audit.",
    forwarder: "TSA/Aeronautics Compliance & Documentation.",
    trucker: "DOT Federal/Florida Safety & Load Distribution.",
    counter: "Receiving & Warehouse Acceptance Criteria."
};

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = content[lang];
    document.getElementById("promoText").innerHTML = t.promo;
    document.getElementById("t_pago").innerText = t.t_pago;
    document.getElementById("t_sol").innerText = t.t_sol;
    document.getElementById("t_cam").innerText = t.t_cam;
    document.getElementById("l_title").innerText = t.l_title;
    document.getElementById("l_desc").innerText = t.l_desc;

    document.getElementById("btnEn").className = lang === 'en' ? 'active-lang' : '';
    document.getElementById("btnEs").className = lang === 'es' ? 'active-lang' : '';
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    document.getElementById('fileInput').onchange = function() {
        const container = document.getElementById('previewContainer');
        container.innerHTML = "";
        Array.from(this.files).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result; img.className = 'thumb';
                container.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    };

    document.querySelectorAll('.profile-btn').forEach(btn => {
        btn.onclick = function() {
            document.querySelectorAll('.profile-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('roleInput').value = this.dataset.role;
        };
    });

    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "GUEST-AUDIT";
        const amt = document.getElementById("priceSelect").value;
        const u = prompt("ADMIN USER:");
        const p = prompt("ADMIN PASS:");

        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(u) fd.append("user", u); if(p) fd.append("password", p);

        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const loader = document.getElementById("loader");
        const out = document.getElementById("advResponse");
        loader.style.display = "block";
        out.innerHTML = "";
        
        const fd = new FormData(e.target);
        const role = document.getElementById('roleInput').value;

        // INSTRUCCIÓN TÉCNICA MAESTRA (Audit Logic)
        const masterPrompt = `You are the Senior Technical Auditor at SmartCargo (May Roga LLC), located in Miami, Florida. 
        MANDATORY KNOWLEDGE: IATA, DOT (Federal/Florida), TSA, FAA, and Maritime regulations. 
        SCOPE: Commercial Freight & Passenger Cargo.
        PROTOCOL:
        1. ANALYZE visual evidence.
        2. IF images are unclear or missing, IMMEDIATELY initiate a technical interview. Ask 3 specific questions (e.g., Weight distribution, HAZMAT presence, Pallet integrity) to guide the client to a solution.
        3. DO NOT act as a chatbot. Act as a Technical Advisor.
        4. DELIVER immediate solutions based on Miami/Florida transport laws.
        ROLE CONTEXT: ${technicalRoles[role]}.
        PURGE POLICY: Do not store or mention sensitive data. No AI mentions.`;

        fd.set("prompt", `${masterPrompt} | Client Input: ${document.getElementById('promptArea').value}`);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `<div id="finalReport" style="border:2px solid var(--navy); padding:20px; margin-top:20px; background:#fff;">
                <h6 style="color:var(--navy); border-bottom:1px solid var(--gold); padding-bottom:5px;">OFFICIAL TECHNICAL ACTION PLAN</h6>
                <p style="white-space: pre-wrap; font-size:13px; color:#1a1a1a;">${data.data}</p>
                <hr>
                <button onclick="window.location.reload()" style="font-size:10px;">PURGE & NEW AUDIT</button>
            </div>`;
            document.getElementById('promptArea').value = ""; // Clear for privacy
        } catch (e) { out.innerHTML = "System Busy. Backup engaged."; }
        finally { loader.style.display = "none"; }
    };
});
