const content = {
    en: {
        banner: "<strong>Benefit:</strong> Avoid fines and cargo damage. Our advisory ensures international compliance.",
        t_scan: "📷 UPLOAD CARGO PHOTOS",
        t_voice: "DESCRIBE BY VOICE",
        t_legal: "Private advisory by May Roga LLC. Not a gov agency.",
        t_reset: "🗑️ DELETE HISTORY & PHOTOS",
        session_msg: "Remaining: "
    },
    es: {
        banner: "<strong>Beneficio:</strong> Evite multas y daños a la carga. Nuestra asesoría asegura el cumplimiento internacional.",
        t_scan: "📷 CARGAR FOTOS DE CARGA",
        t_voice: "DESCRIBIR POR VOZ",
        t_legal: "Asesoría privada de May Roga LLC. No somos agencia gubernamental.",
        t_reset: "🗑️ BORRAR HISTORIAL Y FOTOS",
        session_msg: "Restante: "
    }
};

const TIME_MAP = { "5": 10, "10": 30, "45": 60, "95": 120 };

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = content[lang];
    document.getElementById("mkt_banner").innerHTML = t.banner;
    document.getElementById("t_scan").innerText = t.t_scan;
    document.getElementById("t_voice").innerText = t.t_voice;
    document.getElementById("t_legal").innerText = t.t_legal;
    document.getElementById("t_reset").innerText = t.t_reset;
}

function resetAll() {
    if(confirm("Delete all? / ¿Borrar todo?")) {
        document.getElementById("advResponse").innerHTML = "";
        document.getElementById("previewContainer").innerHTML = "";
        document.getElementById("promptArea").value = "";
        document.getElementById("fileInput").value = "";
        alert("Cleared / Borrado");
    }
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

    // Mostrar Fotos
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

    // Pago / Activación
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "GUEST";
        const amt = document.getElementById("priceSelect").value;
        localStorage.setItem("pending_time", TIME_MAP[amt]);
        
        const u = prompt("ADMIN USER:");
        const p = prompt("ADMIN PASS:");

        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(u) fd.append("user", u); if(p) fd.append("password", p);

        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    // Retorno de Pago y Tiempo
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted") {
        document.getElementById("accessSection").style.display = "none";
        document.getElementById("mainApp").style.display = "block";
        
        const duration = localStorage.getItem("pending_time") || 10;
        const endTime = new Date().getTime() + (duration * 60000);
        
        setInterval(() => {
            const now = new Date().getTime();
            const left = Math.ceil((endTime - now) / 60000);
            if (left <= 0) location.reload();
            document.getElementById("timerDisplay").innerText = "Time: " + left + "m";
        }, 30000);
    }

    document.getElementById("submitBtn").onclick = async () => {
        document.getElementById("loader").style.display = "block";
        const fd = new FormData();
        const files = document.getElementById('fileInput').files;
        Array.from(files).forEach(f => fd.append("files", f));
        fd.append("prompt", document.getElementById("promptArea").value);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        const res = await fetch(`/advisory`, { method: "POST", body: fd });
        const data = await res.json();
        document.getElementById("advResponse").innerHTML = `<div class="report-box">${data.data}</div>`;
        document.getElementById("loader").style.display = "none";
    };
});
