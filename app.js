const content = {
    en: {
        banner: "<strong>May Roga LLC:</strong> Solving million-dollar logistics risks in seconds.",
        t_scan: "📷 UPLOAD EVIDENCE",
        t_voice: "VOICE DESCRIPTION",
        btn_main: "GET SOLUTION NOW"
    },
    es: {
        banner: "<strong>May Roga LLC:</strong> Resolviendo riesgos logísticos millonarios en segundos.",
        t_scan: "📷 CARGAR EVIDENCIA",
        t_voice: "DESCRIPCIÓN POR VOZ",
        btn_main: "OBTENER SOLUCIÓN AHORA"
    }
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

    // ---------------- VOZ ----------------
    if ("webkitSpeechRecognition" in window) {
        const recog = new webkitSpeechRecognition();
        recog.onresult = e => {
            document.getElementById("promptArea").value +=
                e.results[0][0].transcript + " ";
        };
        document.getElementById("voiceBtn").onclick = () => {
            recog.lang = localStorage.getItem("user_lang") === "es" ? "es-ES" : "en-US";
            recog.start();
        };
    }

    // ---------------- PREVIEW IMÁGENES ----------------
    document.getElementById("fileInput").onchange = function () {
        const container = document.getElementById("previewContainer");
        container.innerHTML = "";
        Array.from(this.files).slice(0, 3).forEach(file => {
            const reader = new FileReader();
            reader.onload = e => {
                const img = document.createElement("img");
                img.src = e.target.result;
                container.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    };

    // ---------------- SUBMIT ----------------
    document.getElementById("submitBtn").onclick = async () => {

        if (localStorage.getItem("sc_auth") !== "true") {
            document.getElementById("paymentModal").style.display = "flex";
            return;
        }

        document.getElementById("loader").style.display = "block";

        const fd = new FormData();
        Array.from(document.getElementById("fileInput").files)
            .forEach(f => fd.append("files", f));

        fd.append("prompt", document.getElementById("promptArea").value);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();

        document.getElementById("advResponse").innerHTML =
            `<div class="report-box">${data.data || "No advisory response received."}</div>`;

        document.getElementById("loader").style.display = "none";
    };

    // ---------------- ACTIVACIÓN ----------------
    document.getElementById("activateBtn").onclick = async () => {
        localStorage.setItem("sc_auth", "true");
        document.getElementById("paymentModal").style.display = "none";
    };
});
