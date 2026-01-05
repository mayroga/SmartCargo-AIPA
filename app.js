let selectedRole = "", selectedAmount = 0, currentLang = "en", timeLeft = 0, idleTime = 0;
const ui = { en: { wait: "⚙️ ANALYZING...", alert: "TOUCH TO STAY ACTIVE!" }, es: { wait: "⚙️ ANALIZANDO...", alert: "¡TOQUE PARA SEGUIR ACTIVO!" } };

function setLang(l, el) { currentLang = l; }

function loadPhoto(i) {
    const file = document.getElementById(`f${i}`).files[0];
    if (file) {
        const r = new FileReader();
        r.onload = (e) => { const img = document.getElementById(`p${i}`); img.src = e.target.result; img.style.border = "3px solid #1b5e20"; };
        r.readAsDataURL(file);
    }
}

function startVoice() {
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    rec.lang = currentLang === 'es' ? 'es-ES' : 'en-US';
    rec.onresult = (e) => { document.getElementById("promptArea").value += e.results[0][0].transcript; };
    rec.start();
}

async function getSolution() {
    const out = document.getElementById("advResponse");
    out.innerHTML = `<strong>${ui[currentLang].wait}</strong>`;
    const fd = new FormData();
    fd.append("prompt", `Role: ${selectedRole}. Tier: ${selectedAmount}. Input: ${document.getElementById("promptArea").value}`);
    fd.append("lang", currentLang);
    const res = await fetch("/advisory", { method: "POST", body: fd });
    const data = await res.json();
    out.innerHTML = `<div style="background:#f1f3f5; border-left:6px solid #d4af37; padding:15px; font-size:14px; white-space:pre-wrap;">${data.data}</div>`;
    document.getElementById("btnWs").style.display = "block";
}

function sendWS() {
    const text = document.getElementById("advResponse").innerText;
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent("SmartCargo Solution:\n\n" + text)}`, '_blank');
}

function resetIdle() { idleTime = 0; }
function selRole(v, el) { selectedRole = v; document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }
function selTier(v, el) { selectedAmount = v; document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }

document.addEventListener("DOMContentLoaded", () => {
    const p = new URLSearchParams(window.location.search);
    if(p.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        const t = p.get("tier");
        timeLeft = (t == "95" ? 45 : (t == "35" ? 20 : (t == "15" ? 10 : 4))) * 60;
        setInterval(() => {
            timeLeft--; idleTime++;
            if(idleTime === 59) { alert(ui[currentLang].alert); resetIdle(); }
            document.getElementById("timerDisp").innerHTML = `SESSION ACTIVE: ${Math.floor(timeLeft/60)}:${(timeLeft%60).toString().padStart(2,'0')}`;
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
