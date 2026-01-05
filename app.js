let selectedTier = 0;
let timeLeft = 0;
let timerInt;

const langData = {
    en: { greet: "Hello. What part of the chain are we auditing? Shipper, Trucker or Docs? Tell me your fear.", timeMsg: "Session: " },
    es: { greet: "Hola. ¿Qué parte de la cadena vamos a auditar? ¿Shipper, Transportista o Papeles? Dígame su miedo.", timeMsg: "Sesión: " },
    fr: { greet: "Bonjour. Quelle partie de la chaîne auditons-nous ? Shipper, Transporteur ou Docs ?", timeMsg: "Session: " },
    pt: { greet: "Olá. Que parte da cadeia estamos auditando? Shipper, Motorista ou Docs?", timeMsg: "Sessão: " }
};

function setLang(l) {
    localStorage.setItem("sc_lang", l);
    const lang = langData[l] || langData.en;
    if(document.getElementById("greeting")) document.getElementById("greeting").innerText = lang.greet;
}

function selTier(val, el) {
    selectedTier = val;
    document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
}

function previewFiles() {
    const container = document.getElementById("previewContainer");
    container.innerHTML = "";
    Array.from(document.getElementById("fileInput").files).forEach(f => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement("img"); img.src = e.target.result;
            img.style.width = "65px"; img.style.height = "65px"; img.style.objectFit="cover"; img.style.margin = "5px"; container.appendChild(img);
        };
        reader.readAsDataURL(f);
    });
}

function startTimer(mins) {
    timeLeft = mins * 60;
    const disp = document.getElementById("timerDisp");
    disp.style.display = "block";
    timerInt = setInterval(() => {
        timeLeft--;
        let m = Math.floor(timeLeft / 60);
        let s = timeLeft % 60;
        const l = localStorage.getItem("sc_lang") || "en";
        disp.innerText = `${langData[l].timeMsg} ${m}:${s<10?'0':''}${s}`;
        if(timeLeft === 60) { disp.classList.add("warning-flash"); alert("1 MINUTE LEFT!"); }
        if(timeLeft <= 0) { clearInterval(timerInt); alert("Session Expired."); location.reload(); }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    const lang = localStorage.getItem("sc_lang") || "en";
    setLang(lang);
    
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        const tier = params.get("tier");
        startTimer(tier == "45" ? 20 : (tier == "95" ? 45 : 8));
    }

    // VOZ
    const SpeechSDK = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechSDK) {
        const recognition = new SpeechSDK();
        document.getElementById("voiceBtn").onclick = () => { recognition.start(); };
        recognition.onresult = (e) => { document.getElementById("promptArea").value = e.results[0][0].transcript; };
    }

    document.getElementById("activateBtn").onclick = async () => {
        if(selectedTier === 0) return alert("Select a Tier!");
        const u = prompt("ADMIN USER:");
        const fd = new FormData();
        fd.append("amount", selectedTier);
        fd.append("awb", document.getElementById("awbField").value || "ID");
        if(u) { fd.append("user", u); fd.append("password", prompt("ADMIN PASS:")); }
        const res = await fetch("/create-payment", { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<strong>ANALYZING STEP-BY-STEP...</strong>";
        const fd = new FormData(e.target);
        fd.append("prompt", document.getElementById("promptArea").value);
        fd.append("lang", localStorage.getItem("sc_lang") || "en");
        
        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();
        out.innerHTML = `<div class="report">${data.data}</div>`;
    };
});
