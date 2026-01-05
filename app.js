let selectedRole = "";
let selectedAmount = 0;
let currentLang = "es"; // Por defecto
let timeLeft = 0;
let idleTime = 0;

function setLang(lang, el) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    console.log("Idioma cambiado a: " + lang);
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
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => { 
            const img = document.getElementById("mainPreview");
            img.src = e.target.result; img.style.display = "block";
        };
        reader.readAsDataURL(file);
    }
}

function startTimer(mins, tier) {
    // Regla de 4 minutos para pagos de 5 y 10
    let effectiveMins = (tier == "5" || tier == "10") ? 4 : mins;
    timeLeft = effectiveMins * 60;
    
    const disp = document.getElementById("timerDisp");
    setInterval(() => {
        timeLeft--;
        idleTime++;
        
        // Advertencia de 59 segundos
        if (idleTime === 59) {
            alert("⚠️ TOQUE LA PANTALLA para mantener la sesión activa.");
            resetIdle();
        }

        let m = Math.floor(timeLeft / 60);
        let s = timeLeft % 60;
        disp.innerText = `SESIÓN ACTIVA: ${m}:${s < 10 ? '0' : ''}${s}`;
        
        if (timeLeft <= 0) location.reload();
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        
        const tier = params.get("tier");
        const baseMins = (tier == "45") ? 20 : (tier == "95" ? 45 : 8);
        startTimer(baseMins, tier);
    }

    document.getElementById("activateBtn").onclick = async () => {
        if(!selectedRole || selectedAmount === 0) return alert("Seleccione Rol e Idioma.");
        const fd = new FormData();
        fd.append("amount", selectedAmount);
        fd.append("awb", document.getElementById("awbField").value || "AUDIT");
        
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
        out.innerHTML = "<strong>⚙️ ANALIZANDO...</strong>";
        
        const fd = new FormData();
        fd.append("prompt", `Soy el ${selectedRole}. Problema: ${document.getElementById("promptArea").value}`);
        fd.append("lang", currentLang); // Envía el idioma seleccionado
        
        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();
        out.innerHTML = `<div class="report">${data.data}</div>`;
    };
});
