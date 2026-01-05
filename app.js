let selectedRole = "";
let selectedAmount = 0;
let currentLang = "es"; 
let timeLeft = 0;
let idleTime = 0;
let timerInterval;

// Traducciones para el sistema de interfaz
const uiLang = {
    es: { greeting: "Hola. Vamos a revisar y chequear este caso juntos. ¿Qué es lo primero que quieres que rectifiquemos?", wait: "⚙️ ASESOR ANALIZANDO...", alert: "⚠️ TOQUE LA PANTALLA para mantener la asesoría activa." },
    en: { greeting: "Hello. Let's check and review this case together. What's the first thing you want to rectify?", wait: "⚙️ ADVISOR ANALYZING...", alert: "⚠️ TOUCH SCREEN to keep the session active." },
    fr: { greeting: "Bonjour. Vérifions et examinons ce cas ensemble. Quelle est la première chose que vous voulez rectifier?", wait: "⚙️ ANALYSE EN COURS...", alert: "⚠️ TOUCHEZ L'ÉCRAN para maintenir la session active." },
    pt: { greeting: "Olá. Vamos conferir e revisar este caso juntos. Qual é a primeira coisa que você deseja retificar?", wait: "⚙️ ASSESSOR ANALISANDO...", alert: "⚠️ TOQUE NA TELA para manter a sessão ativa." }
};

function setLang(lang, el) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
}

function resetIdle() { idleTime = 0; }

function selRole(val, el) { 
    selectedRole = val; 
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); 
    el.classList.add('selected'); 
}

function selTier(val, el) { 
    selectedAmount = val; 
    document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected')); 
    el.classList.add('selected'); 
}

function showPreview() {
    const file = document.getElementById("fileInput").files[0];
    const preview = document.getElementById("mainPreview");
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => { 
            preview.src = e.target.result; 
            preview.style.display = "block";
        };
        reader.readAsDataURL(file);
    }
}

function startTimer(mins, tier) {
    let effectiveMins = (tier == "5" || tier == "10") ? 4 : mins;
    timeLeft = effectiveMins * 60;
    
    const disp = document.getElementById("timerDisp");
    timerInterval = setInterval(() => {
        timeLeft--;
        idleTime++;
        
        if (idleTime === 59) {
            alert(uiLang[currentLang].alert);
            resetIdle();
        }

        let m = Math.floor(timeLeft / 60);
        let s = timeLeft % 60;
        disp.innerText = `SESIÓN ACTIVA: ${m}:${s < 10 ? '0' : ''}${s}`;
        
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            location.href = "/";
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    
    if (params.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        
        // Mostrar saludo inicial según idioma
        const welcomeOut = document.getElementById("advResponse");
        welcomeOut.innerHTML = `<div class="report">${uiLang[currentLang].greeting}</div>`;
        
        const tier = params.get("tier");
        const baseMins = (tier == "45") ? 20 : (tier == "95" ? 45 : 8);
        startTimer(baseMins, tier);
    }

    document.getElementById("activateBtn").onclick = async () => {
        if(!selectedRole || selectedAmount === 0) return alert("Seleccione Rol, Nivel e Idioma.");
        
        const fd = new FormData();
        const awbVal = document.getElementById("awbField").value || "REVISIÓN";
        fd.append("amount", selectedAmount);
        fd.append("awb", awbVal);
        
        const u = prompt("ADMIN USER (Opcional):");
        if(u) {
            fd.append("user", u);
            fd.append("password", prompt("ADMIN PASS:"));
        }

        const res = await fetch("/create-payment", { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        const btnSubmit = e.target.querySelector('button[type="submit"]');
        const awbActual = new URLSearchParams(window.location.search).get("awb") || "N/A";
        
        btnSubmit.disabled = true;
        out.innerHTML = `<strong>${uiLang[currentLang].wait}</strong>`;
        
        const fd = new FormData();
        fd.append("prompt", `[REF: ${awbActual}] Soy el ${selectedRole}. Consulta: ${document.getElementById("promptArea").value}`);
        fd.append("lang", currentLang);
        
        try {
            const res = await fetch("/advisory", { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `<div class="report">${data.data}</div>`;
        } catch (err) {
            out.innerHTML = "Error de conexión. Intente de nuevo.";
        } finally {
            btnSubmit.disabled = false;
        }
    };
});
