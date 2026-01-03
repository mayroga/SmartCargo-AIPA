const content = {
    en: {
        promo: "<strong>Cargo Protection:</strong> Technical advisory to mitigate risks. 2-Hour Maximum Window.",
        t_activation: "1. SERVICE ACTIVATION",
        t_solutions: "2. TECHNICAL ADVISORY CENTER",
        t_scan: "📷 SCAN CARGO / DOCUMENTS",
        t_compliance: "Technical Advisory | International Standards",
        i_title: "INSPECTION PROTOCOL",
        i_body: "For a precise advisory, upload at least 3 photos:<br><strong>1. Front View:</strong> Stability.<br><strong>2. Side View:</strong> Structure.<br><strong>3. Labels & Seals:</strong> ID and Compliance.",
        legal: "<strong>LEGAL NOTICE:</strong> Private technical advisory by May Roga LLC. Not a government agency. Information for risk mitigation purposes only.",
        btn_wa: "🟢 SEND TO WHATSAPP",
        btn_clear: "🗑️ CLEAR & NEXT",
        session_msg: "Access Time Left:"
    },
    es: {
        promo: "<strong>Protección de Carga:</strong> Asesoría técnica para mitigar riesgos. Ventana Máxima de 2 Horas.",
        t_activation: "1. ACTIVACIÓN DE SERVICIO",
        t_solutions: "2. CENTRO DE ASESORÍA TÉCNICA",
        t_scan: "📷 ESCANEAR CARGA / PAPELES",
        t_compliance: "Asesoría Técnica | Normas Internacionales",
        i_title: "PROTOCOLO DE INSPECCIÓN",
        i_body: "Para una asesoría precisa, suba al menos 3 fotos:<br><strong>1. Frontal:</strong> Estabilidad.<br><strong>2. Lateral:</strong> Estructura.<br><strong>3. Etiquetas/Sellos:</strong> Identificación.",
        legal: "<strong>AVISO LEGAL:</strong> Asesoría técnica privada de May Roga LLC. No somos agencia gubernamental. Información solo para mitigación de riesgos.",
        btn_wa: "🟢 ENVIAR POR WHATSAPP",
        btn_clear: "🗑️ LIMPIAR Y SEGUIR",
        session_msg: "Tiempo de Acceso Restante:"
    }
};

const TIME_MAP = { "5": 10, "10": 30, "45": 60, "95": 120 };

async function processImage(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = (e) => {
            const img = new Image();
            img.src = e.target.result;
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const MAX_WIDTH = 1200;
                let width = img.width; let height = img.height;
                if (width > MAX_WIDTH) { height *= MAX_WIDTH / width; width = MAX_WIDTH; }
                canvas.width = width; canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.8);
            };
        };
    });
}

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = content[lang];
    document.getElementById("promo").innerHTML = t.promo;
    document.getElementById("t_activation").innerText = t.t_activation;
    document.getElementById("t_solutions").innerText = t.t_solutions;
    document.getElementById("t_scan").innerText = t.t_scan;
    document.getElementById("t_compliance").innerText = t.t_compliance;
    document.getElementById("i_title").innerText = t.i_title;
    document.getElementById("i_body").innerHTML = t.i_body;
    document.getElementById("legal").innerHTML = t.legal;
}

function resetApp() {
    document.getElementById("advResponse").innerHTML = "";
    document.getElementById("previewContainer").innerHTML = "";
    document.getElementById("promptArea").value = "";
    document.getElementById("fileInput").value = "";
}

function unlockApp() {
    document.getElementById("mainApp").style.opacity = "1";
    document.getElementById("mainApp").style.pointerEvents = "all";
    document.getElementById("accessSection").style.display = "none";
}

function checkSession() {
    const authTime = localStorage.getItem("sc_auth_time");
    const duration = localStorage.getItem("sc_auth_duration");
    const isAuth = localStorage.getItem("sc_auth") === "true";
    if (isAuth && authTime && duration) {
        const now = new Date().getTime();
        const limit = parseInt(duration) * 60 * 1000;
        const elapsed = now - parseInt(authTime);
        if (elapsed > limit) {
            localStorage.clear();
            alert("TIME EXPIRED.");
            location.reload();
        } else {
            unlockApp();
            const remaining = Math.ceil((limit - elapsed) / 60000);
            document.getElementById("sessionTimer").style.display = "block";
            document.getElementById("sessionMins").innerText = remaining;
            document.getElementById("sessionMsg").innerText = content[localStorage.getItem("user_lang") || "en"].session_msg;
        }
    }
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
                img.src = e.target.result;
                container.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    };

    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.onclick = function() {
            document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('roleInput').value = this.dataset.role;
        };
    });

    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "GUEST";
        const amt = document.getElementById("priceSelect").value;
        const u = prompt("ADMIN USER:");
        const p = prompt("ADMIN PASS:");
        localStorage.setItem("sc_pending_duration", TIME_MAP[amt]);
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
        const fd = new FormData();
        const lang = localStorage.getItem("user_lang") || "en";
        const files = document.getElementById('fileInput').files;
        for (let i = 0; i < files.length; i++) {
            const blob = await processImage(files[i]);
            fd.append("files", blob, `cargo_${i}.jpg`);
        }
        const masterPrompt = `Senior Technical Advisor (May Roga LLC). Private Advisory Service. Analyze all views.`;
        fd.append("prompt", `${masterPrompt} | Cargo Details: ${document.getElementById('promptArea').value}`);
        fd.append("lang", lang);
        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `
                <div class="report-box" id="finalReport">
                    <h6 style="color:#001a35; border-bottom:1.5px solid #d4af37; margin-top:0;">TECHNICAL ACTION PLAN</h6>
                    <p style="white-space: pre-wrap; font-size:13px; color:#121212;">${data.data}</p>
                    <button class="whatsapp-btn" onclick="shareWA()">${content[lang].btn_wa}</button>
                    <button class="clear-btn" onclick="resetApp()">${content[lang].btn_clear}</button>
                </div>`;
        } catch (err) { out.innerHTML = "Error."; }
        finally { loader.style.display = "none"; }
    };

    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted") {
        localStorage.setItem("sc_auth", "true");
        localStorage.setItem("sc_auth_time", new Date().getTime().toString());
        localStorage.setItem("sc_auth_duration", localStorage.getItem("sc_pending_duration") || 10);
        unlockApp();
    }
    checkSession();
    setInterval(checkSession, 30000);
});

function shareWA() {
    const text = document.getElementById("finalReport").innerText.split('🟢')[0];
    window.open(`https://wa.me/?text=${encodeURIComponent("SmartCargo Advisory:\n\n" + text)}`, '_blank');
}
