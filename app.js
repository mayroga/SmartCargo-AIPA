let selectedRole = "";
let selectedAmount = 0;
let currentLang = "en";
let timeLeft = 0;
let idleTime = 0;

const ui = {
    en: { role: "1. USER ROLE:", tier: "2. SERVICE TIER:", ref: "Reference / AWB / BOL", btn: "VALIDATE AND ACCESS", scan: "📸 SCAN / UPLOAD PHOTO (OPTIONAL)", solve: "GET SOLUTION", prompt: "Describe what you want to check...", wait: "⚙️ ANALYZING SCENARIOS...", alert: "⚠️ TOUCH SCREEN to keep session active.", reset: "RESET / NEW CHECK" },
    es: { role: "1. ROL DEL USUARIO:", tier: "2. NIVEL DE SERVICIO:", ref: "Referencia / AWB / BOL", btn: "VALIDAR Y ACCEDER", scan: "📸 ESCANEAR / SUBIR FOTO (OPCIONAL)", solve: "OBTENER SOLUCIÓN", prompt: "Describe lo que quieres chequear...", wait: "⚙️ CHEQUEANDO ESCENARIOS...", alert: "⚠️ TOQUE LA PANTALLA para mantener la sesión activa.", reset: "REINICIAR / NUEVA CONSULTA" }
};

function setLang(lang, el) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    document.getElementById("lblRole").innerText = ui[lang].role;
    document.getElementById("lblTier").innerText = ui[lang].tier;
    document.getElementById("awbField").placeholder = ui[lang].ref;
    document.getElementById("activateBtn").innerText = ui[lang].btn;
    document.getElementById("txtScan").innerText = ui[lang].scan;
    document.getElementById("promptArea").placeholder = ui[lang].prompt;
    document.getElementById("btnSolve").innerText = ui[lang].solve;
    document.getElementById("btnReset").innerText = ui[lang].reset;
}

function showPreview() {
    const file = document.getElementById("fileInput").files[0];
    const preview = document.getElementById("mainPreview");
    const container = document.getElementById("previewContainer");
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            container.style.display = "block";
        };
        reader.readAsDataURL(file);
    }
}

function clearAll() {
    document.getElementById("promptArea").value = "";
    document.getElementById("advResponse").innerHTML = "";
    document.getElementById("previewContainer").style.display = "none";
    document.getElementById("mainPreview").src = "";
    document.getElementById("fileInput").value = "";
    document.getElementById("txtScan").innerText = ui[currentLang].scan;
}

function resetIdle() { idleTime = 0; }
function selRole(val, el) { selectedRole = val; document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }
function selTier(val, el) { selectedAmount = val; document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        let tier = params.get("tier");
        let mins = (tier == "45") ? 20 : (tier == "95" ? 45 : 8);
        if (tier == "5" || tier == "10") mins = 4;
        timeLeft = mins * 60;
        setInterval(() => {
            timeLeft--; idleTime++;
            if(idleTime === 59) { alert(ui[currentLang].alert); resetIdle(); }
            let m = Math.floor(timeLeft/60), s = timeLeft%60;
            document.getElementById("timerDisp").innerText = `ACTIVE SESSION: ${m}:${s<10?'0':''}${s}`;
            if(timeLeft <= 0) location.href="/";
        }, 1000);
    }

    document.getElementById("activateBtn").onclick = async () => {
        if(!selectedRole || selectedAmount === 0) return alert("Select Role and Tier");
        const fd = new FormData();
        fd.append("amount", selectedAmount);
        fd.append("awb", document.getElementById("awbField").value || "CHECK");
        const res = await fetch("/create-payment", { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = `<strong>${ui[currentLang].wait}</strong>`;
        const fd = new FormData();
        fd.append("prompt", `Role: ${selectedRole}. Issue: ${document.getElementById("promptArea").value}`);
        fd.append("lang", currentLang);
        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();
        out.innerHTML = `<div class="report">${data.data}</div>`;
    };
});
