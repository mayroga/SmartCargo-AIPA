let selectedAmount = 0;
let timeLeft = 0;
let timerInterval;

const langData = {
    es: { greet: "Hola. ¿Qué desea auditar hoy? ¿Shipper, Transportista o Papeles? Dígame su miedo para resolverlo.", timeMsg: "Tiempo Restante: " },
    en: { greet: "Hello. What are we auditing? Shipper, Trucker or Docs? Tell me your fear to solve it.", timeMsg: "Time Left: " }
};

function selectTier(amt, el) {
    selectedAmount = amt;
    document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
}

function startTimer(minutes) {
    timeLeft = minutes * 60;
    const display = document.getElementById("timerDisplay");
    display.style.display = "block";

    timerInterval = setInterval(() => {
        let mins = Math.floor(timeLeft / 60);
        let secs = timeLeft % 60;
        display.innerHTML = `${langData[localStorage.getItem("sc_lang") || "es"].timeMsg} ${mins}:${secs < 10 ? '0' : ''}${secs}`;
        
        if (timeLeft === 60) {
            display.classList.add("warning-flash");
            alert("AVISO: Le queda 1 minuto de asesoría.");
        }

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            alert("Sesión finalizada. Reiniciando sistema...");
            localStorage.removeItem("sc_auth");
            window.location.href = "/";
        }
        timeLeft--;
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const tier = params.get("tier");
    const lang = localStorage.getItem("sc_lang") || "es";
    
    document.getElementById("greeting").innerText = langData[lang].greet;

    if (params.get("access") === "granted") {
        localStorage.setItem("sc_auth", "true");
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        
        let duration = (tier == "45") ? 20 : (tier == "95" ? 45 : 8);
        startTimer(duration);
    }

    // VOZ
    const voiceBtn = document.getElementById("voiceBtn");
    const SpeechSDK = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechSDK) {
        const recognition = new SpeechSDK();
        recognition.lang = lang === "es" ? "es-US" : "en-US";
        voiceBtn.onclick = () => { recognition.start(); voiceBtn.innerText = "Escuchando..."; };
        recognition.onresult = (e) => { 
            document.getElementById("promptArea").value = e.results[0][0].transcript;
            voiceBtn.innerText = "🎤 HABLAR PROBLEMA";
        };
    }

    // FOTOS
    document.getElementById('fileInput').onchange = function() {
        const container = document.getElementById('previewContainer');
        container.innerHTML = "";
        Array.from(this.files).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img'); img.src = e.target.result;
                img.className = "preview-img"; container.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    };

    // BOTÓN ACTIVAR
    document.getElementById("activateBtn").onclick = async () => {
        if(selectedAmount === 0) { alert("Por favor, seleccione un nivel de precio."); return; }
        const fd = new FormData();
        fd.append("amount", selectedAmount);
        fd.append("awb", document.getElementById("awbField").value || "AUDIT");
        const u = prompt("ADMIN USER (Opcional):");
        if(u) { fd.append("user", u); fd.append("password", prompt("ADMIN PASS:")); }

        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    // SOLUCIÓN
    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<strong>⚙️ GENERANDO PLAN DE ACCIÓN...</strong>";
        const fd = new FormData();
        Array.from(document.getElementById('fileInput').files).forEach(f => fd.append("files", f));
        fd.append("prompt", document.getElementById("promptArea").value);
        fd.append("lang", lang);

        const res = await fetch(`/advisory`, { method: "POST", body: fd });
        const data = await res.json();
        out.innerHTML = `<div class="report">${data.data}</div>`;
    };
});
