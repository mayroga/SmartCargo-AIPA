let selectedRole = "", selectedAmount = 0, currentLang = "en", timeLeft = 0, idleTime = 0;
const ui = {
    en: { wait: "⚙️ ANALYZING SCENARIO...", alert: "TOUCH TO REMAIN ACTIVE!" },
    es: { wait: "⚙️ ANALIZANDO ESCENARIO...", alert: "¡TOQUE PARA SEGUIR ACTIVO!" }
};

function setLang(l, el) { currentLang = l; document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active')); el.classList.add('active'); }

function loadPhotos() {
    const files = document.getElementById('fileInput').files;
    for(let i=0; i<3; i++) {
        const img = document.getElementById(`p${i+1}`);
        if(files[i]) {
            const r = new FileReader();
            r.onload = (e) => { img.src = e.target.result; img.style.display = "block"; };
            r.readAsDataURL(files[i]);
        }
    }
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = currentLang === 'es' ? 'es-ES' : 'en-US';
    recognition.onresult = (e) => { document.getElementById("promptArea").value = e.results[0][0].transcript; };
    recognition.start();
}

async function getSolution() {
    const out = document.getElementById("advResponse");
    out.innerHTML = `<strong>${ui[currentLang].wait}</strong>`;
    const fd = new FormData();
    fd.append("prompt", `Role: ${selectedRole}. Technical Issue: ${document.getElementById("promptArea").value}`);
    fd.append("lang", currentLang);
    const res = await fetch("/advisory", { method: "POST", body: fd });
    const data = await res.json();
    out.innerHTML = `<div class="report">${data.data}</div>`;
    document.getElementById("btnWs").style.display = "block";
}

function sendWS() {
    const text = document.getElementById("advResponse").innerText;
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent("SmartCargo Advisory (May Roga LLC):\n\n" + text)}`, '_blank');
}

function resetIdle() { idleTime = 0; }
function selRole(v, el) { selectedRole = v; document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }
function selTier(v, el) { selectedAmount = v; document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }

document.addEventListener("DOMContentLoaded", () => {
    const p = new URLSearchParams(window.location.search);
    if(p.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        timeLeft = (p.get("tier") == "95" ? 45 : 4) * 60;
        setInterval(() => {
            timeLeft--; idleTime++;
            if(idleTime === 59) { alert(ui[currentLang].alert); resetIdle(); }
            document.getElementById("timerDisp").innerText = `SESSION ACTIVE: ${Math.floor(timeLeft/60)}:${(timeLeft%60).toString().padStart(2,'0')}`;
            if(timeLeft <= 0) location.href="/";
        }, 1000);
    }
    document.getElementById("activateBtn").onclick = async () => {
        if(!selectedRole || selectedAmount === 0) return alert("Select Role & Tier");
        const fd = new FormData();
        fd.append("amount", selectedAmount); fd.append("awb", document.getElementById("awbField").value || "CHECK");
        const u = prompt("ADMIN?"); if(u) { fd.append("user", u); fd.append("password", prompt("PASS?")); }
        const res = await fetch("/create-payment", { method: "POST", body: fd });
        const data = await res.json(); if(data.url) window.location.href = data.url;
    };
});
