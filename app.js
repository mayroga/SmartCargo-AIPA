const content = {
    en: { banner: "<strong>May Roga LLC:</strong> Solving million-dollar logistics risks in seconds. Practical, direct technical solutions.", t_scan: "📷 UPLOAD EVIDENCE", t_voice: "VOICE DESCRIPTION", btn_main: "GET SOLUTION NOW" },
    es: { banner: "<strong>May Roga LLC:</strong> Resolviendo riesgos logísticos millonarios en segundos. Soluciones técnicas prácticas y directas.", t_scan: "📷 CARGAR EVIDENCIA", t_voice: "DESCRIPCIÓN POR VOZ", btn_main: "OBTENER SOLUCIÓN AHORA" }
};

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = content[lang];
    document.getElementById("mkt_banner").innerHTML = t.banner;
    document.getElementById("t_scan").innerText = t.t_scan;
    document.getElementById("t_voice").innerText = t.t_voice;
    document.getElementById("submitBtn").innerText = t.btn_main;
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");
    const voiceBtn = document.getElementById("voiceBtn");
    if ('webkitSpeechRecognition' in window) {
        const recog = new webkitSpeechRecognition();
        recog.onresult = (e) => { document.getElementById("promptArea").value += e.results[0][0].transcript + " "; };
        voiceBtn.onclick = () => { recog.lang = localStorage.getItem("user_lang") === "es" ? "es-ES" : "en-US"; recog.start(); };
    }
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
    document.getElementById("submitBtn").onclick = async () => {
        if (localStorage.getItem("sc_auth") !== "true") {
            document.getElementById("paymentModal").style.display = "flex";
            return;
        }
        const loader = document.getElementById("loader");
        loader.style.display = "block";
        const fd = new FormData();
        Array.from(document.getElementById('fileInput').files).forEach(f => fd.append("files", f));
        fd.append("prompt", document.getElementById("promptArea").value);
        fd.append("lang", localStorage.getItem("user_lang") || "en");
        const res = await fetch(`/advisory`, { method: "POST", body: fd });
        const data = await res.json();
        document.getElementById("advResponse").innerHTML = `<div class="report-box">${data.data}</div>`;
        loader.style.display = "none";
    };
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "GUEST";
        const amt = document.getElementById("priceSelect").value;
        const u = prompt("ADMIN USER:"); const p = prompt("ADMIN PASS:");
        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(u) fd.append("user", u); if(p) fd.append("password", p);
        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };
    if (new URLSearchParams(window.location.search).get("access") === "granted") {
        localStorage.setItem("sc_auth", "true");
        window.history.replaceState({}, document.title, "/");
    }
});
