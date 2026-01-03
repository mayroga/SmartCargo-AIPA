const content = {
    en: {
        banner: "<strong>May Roga LLC:</strong> We prevent DOT fines and cargo damages. Use our scanner and voice advisory to protect your freight.",
        t_scan: "📷 UPLOAD CARGO PHOTOS", t_voice: "DESCRIBE BY VOICE",
        t_legal: "Private Advisory by May Roga LLC. Not a government agency.",
        t_reset: "🗑️ DELETE HISTORY", btn_main: "EXECUTE ADVISORY"
    },
    es: {
        banner: "<strong>May Roga LLC:</strong> Prevenimos multas del DOT y daños. Use nuestro escáner y asesoría de voz para proteger su carga.",
        t_scan: "📷 CARGAR FOTOS", t_voice: "DESCRIBIR POR VOZ",
        t_legal: "Asesoría Privada de May Roga LLC. No somos agencia gubernamental.",
        t_reset: "🗑️ BORRAR TODO", btn_main: "EJECUTAR ASESORÍA"
    }
};

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = content[lang];
    document.getElementById("mkt_banner").innerHTML = t.banner;
    document.getElementById("t_scan").innerText = t.t_scan;
    document.getElementById("t_voice").innerText = t.t_voice;
    document.getElementById("t_legal").innerText = t.t_legal;
    document.getElementById("t_reset").innerText = t.t_reset;
    document.getElementById("submitBtn").innerText = t.btn_main;
}

function resetApp() {
    if(confirm("¿Borrar todo?")) { localStorage.clear(); location.reload(); }
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    // Lógica de Voz
    const voiceBtn = document.getElementById("voiceBtn");
    if ('webkitSpeechRecognition' in window) {
        const recog = new webkitSpeechRecognition();
        recog.onresult = (e) => { document.getElementById("promptArea").value += e.results[0][0].transcript + " "; };
        voiceBtn.onclick = () => { recog.lang = localStorage.getItem("user_lang") === "es" ? "es-ES" : "en-US"; recog.start(); };
    }

    // Visualización de Fotos para generar curiosidad
    document.getElementById('fileInput').onchange = function() {
        const container = document.getElementById('previewContainer');
        container.innerHTML = "";
        Array.from(this.files).slice(0, 3).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                container.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    };

    // BOTÓN PRINCIPAL
    document.getElementById("submitBtn").onclick = async () => {
        const isAuth = localStorage.getItem("sc_auth") === "true";
        
        // Si no ha pagado, mostramos el modal de pago
        if (!isAuth) {
            document.getElementById("paymentModal").style.display = "flex";
            return;
        }

        // Si ya pagó, ejecutamos la asesoría
        executeAdvisory();
    };

    // Lógica del Botón dentro del Modal (Stripe / Admin)
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "GUEST";
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

    // Al volver de Stripe
    if (new URLSearchParams(window.location.search).get("access") === "granted") {
        localStorage.setItem("sc_auth", "true");
        // Limpiar URL
        window.history.replaceState({}, document.title, "/");
    }
});

async function executeAdvisory() {
    const loader = document.getElementById("loader");
    loader.style.display = "block";
    const fd = new FormData();
    const files = document.getElementById('fileInput').files;
    Array.from(files).forEach(f => fd.append("files", f));
    fd.append("prompt", document.getElementById("promptArea").value);
    fd.append("lang", localStorage.getItem("user_lang") || "en");

    const res = await fetch(`/advisory`, { method: "POST", body: fd });
    const data = await res.json();
    document.getElementById("advResponse").innerHTML = `<div class="report-box">${data.data}</div>`;
    loader.style.display = "none";
}
