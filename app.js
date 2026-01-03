const content = {
    en: { t_scan: "📷 UPLOAD VISUAL EVIDENCE", t_protocol: "Front • Side • Labels", t_voice: "DESCRIBE BY VOICE", t_legal: "Private technical advisory by May Roga LLC. Not a gov agency.", btn_main: "EXECUTE ADVISORY" },
    es: { t_scan: "📷 CARGAR EVIDENCIA VISUAL", t_protocol: "Frente • Lado • Etiquetas", t_voice: "DESCRIBIR POR VOZ", t_legal: "Asesoría técnica privada de May Roga LLC. No somos agencia gubernamental.", btn_main: "EJECUTAR ASESORÍA" }
};

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = content[lang];
    document.getElementById("t_scan").innerText = t.t_scan;
    document.getElementById("t_protocol").innerText = t.t_protocol;
    document.getElementById("t_voice").innerText = t.t_voice;
    document.getElementById("t_legal").innerText = t.t_legal;
    document.getElementById("submitBtn").innerText = t.btn_main;
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    // Lógica de Voz (Web Speech API)
    const voiceBtn = document.getElementById("voiceBtn");
    const promptArea = document.getElementById("promptArea");

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recog = new Recognition();
        recog.lang = localStorage.getItem("user_lang") === "es" ? "es-ES" : "en-US";
        
        voiceBtn.onclick = () => {
            recog.start();
            voiceBtn.style.background = "#ffeb3b";
            voiceBtn.style.color = "#000";
        };

        recog.onresult = (e) => {
            promptArea.value += e.results[0][0].transcript + " ";
            voiceBtn.style.background = "#d32f2f";
            voiceBtn.style.color = "#fff";
        };
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

    document.getElementById("activateBtn").onclick = () => {
        document.getElementById("accessSection").style.display = "none";
        document.getElementById("mainApp").style.display = "block";
    };

    document.getElementById("submitBtn").onclick = async () => {
        const loader = document.getElementById("loader");
        const out = document.getElementById("advResponse");
        loader.style.display = "block";
        out.innerHTML = "";

        const fd = new FormData();
        const files = document.getElementById('fileInput').files;
        Array.from(files).forEach(f => fd.append("files", f));
        fd.append("prompt", promptArea.value);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `<div class="report-box"><strong>ADVISORY REPORT:</strong>\n${data.data}</div>`;
        } catch (e) { out.innerHTML = "Connection Error."; }
        finally { loader.style.display = "none"; }
    };
});
