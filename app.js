const content = {
    en: {
        promo: "<strong>Cargo Protection:</strong> We audit the entire logistics chain (Sea, Land, Air) to prevent fines, holds, and damages. From Shipper to Final Operator.",
        t_scan: "📷 SCAN CARGO / DOCUMENTS",
        legal: "<strong>LEGAL DISCLAIMER:</strong> SmartCargo by May Roga LLC is a PRIVATE advisory service. We are NOT government agents (TSA/CBP). We do NOT touch or certify cargo. Suggestions are based on international standards to mitigate financial risks."
    },
    es: {
        promo: "<strong>Protección de Carga:</strong> Auditamos toda la cadena (Mar, Tierra, Aire) para evitar multas y daños. Del Shipper al Operador Final.",
        t_scan: "📷 ESCANEAR CARGA / PAPELES",
        legal: "<strong>AVISO LEGAL:</strong> SmartCargo de May Roga LLC es asesoría PRIVADA. NO somos agentes del gobierno. NO tocamos ni certificamos carga. Sugerencias basadas en normas internacionales."
    }
};

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = content[lang];
    document.getElementById("promo").innerHTML = t.promo;
    document.getElementById("t_scan").innerText = t.t_scan;
    document.getElementById("legal").innerHTML = t.legal;
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    // Manejo de Fotos
    document.getElementById('fileInput').onchange = function() {
        const container = document.getElementById('previewContainer');
        container.innerHTML = "";
        Array.from(this.files).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                container.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    };

    // Selección de Roles
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.onclick = function() {
            document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('roleInput').value = this.dataset.role;
        };
    });

    // ACTIVACIÓN (ADMIN INCLUIDO)
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "INTERNAL-AUDIT";
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

    // GENERAR SOLUCIÓN
    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const loader = document.getElementById("loader");
        const out = document.getElementById("advResponse");
        loader.style.display = "block";
        out.innerHTML = "";

        const fd = new FormData(e.target);
        const role = document.getElementById('roleInput').value;

        // INSTRUCCIÓN MAESTRA TÉCNICA
        const masterPrompt = `Senior Advisor at SmartCargo (May Roga LLC). 
        CONTEXT: Audit cargo in the logistics chain (Air, Sea, Land). 
        LAWS: IATA, DOT, TSA, Maritime. 
        MISION: Prevent fines and holds. If photos are not clear, ASK technical questions (weight, HAZMAT, pallet type). 
        ROLE: ${role}. Provide IMMEDIATE SOLUTIONS. No AI mentions. Private Advisory Only.`;

        fd.set("prompt", `${masterPrompt} | Cargo Details: ${document.getElementById('promptArea').value}`);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `<div style="border:2px solid #001a35; padding:15px; margin-top:15px;">
                <h6 style="color:#001a35; border-bottom:1px solid #d4af37;">TECHNICAL ACTION PLAN</h6>
                <p style="white-space: pre-wrap; font-size:13px;">${data.data}</p>
                <button onclick="window.location.reload()" style="font-size:9px;">CLEAR SESSION</button>
            </div>`;
        } catch (e) { out.innerHTML = "System Error. Check connection."; }
        finally { loader.style.display = "none"; }
    };

    // Verificar si ya tiene acceso
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        document.getElementById("mainApp").style.opacity = "1";
        document.getElementById("mainApp").style.pointerEvents = "all";
        document.getElementById("accessSection").style.display = "none";
    }
});
