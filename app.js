let selectedRole = "";
let selectedAmount = 0;
let currentLang = "es"; 
let timeLeft = 0;
let idleTime = 0;

function setLang(lang, el) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    // Actualizar textos de la interfaz si es necesario
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

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        let mins = (params.get("tier") == "45") ? 20 : (params.get("tier") == "95" ? 45 : 8);
        if (params.get("tier") == "5" || params.get("tier") == "10") mins = 4;
        
        timeLeft = mins * 60;
        setInterval(() => {
            timeLeft--; idleTime++;
            if(idleTime === 59) { alert("Toque la pantalla para seguir."); resetIdle(); }
            let m = Math.floor(timeLeft/60), s = timeLeft%60;
            document.getElementById("timerDisp").innerText = `SESIÓN ACTIVA: ${m}:${s<10?'0':''}${s}`;
            if(timeLeft <= 0) location.href="/";
        }, 1000);
    }

    document.getElementById("activateBtn").onclick = async () => {
        if(!selectedRole || selectedAmount === 0) return alert("Seleccione Rol y Nivel.");
        const fd = new FormData();
        fd.append("amount", selectedAmount);
        fd.append("awb", document.getElementById("awbField").value || "REVISIÓN");
        
        const u = prompt("ADMIN?");
        if(u) { fd.append("user", u); fd.append("password", prompt("PASS?")); }

        const res = await fetch("/create-payment", { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
        else alert("Error en Stripe: " + (data.error || "Desconocido"));
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<strong>⚙️ CHEQUEANDO DATOS...</strong>";
        const fd = new FormData();
        fd.append("prompt", `Rol: ${selectedRole}. Consulta: ${document.getElementById("promptArea").value}`);
        fd.append("lang", currentLang); 
        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();
        out.innerHTML = `<div class="report">${data.data}</div>`;
    };
});
