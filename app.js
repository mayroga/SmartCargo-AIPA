let selectedRole = "";
let selectedAmount = 0;
let timeLeft = 0;
let idleTime = 0;
let timerInterval;

function resetIdle() { idleTime = 0; }
function selRole(val, el) { selectedRole = val; document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }
function selTier(val, el) { selectedAmount = val; document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }

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
    // REGLA: $5 y $10 mueren a los 4 minutos
    let effectiveMins = (tier == "5" || tier == "10") ? 4 : mins;
    timeLeft = effectiveMins * 60;
    const disp = document.getElementById("timerDisp");
    
    timerInterval = setInterval(() => {
        timeLeft--;
        idleTime++;
        if (idleTime === 59) { alert("⚠️ INACTIVITY ALERT: Touch screen to keep session!"); resetIdle(); }
        
        let m = Math.floor(timeLeft / 60);
        let s = timeLeft % 60;
        disp.innerText = `SESSION ACTIVE: ${m}:${s < 10 ? '0' : ''}${s}`;
        
        if (timeLeft <= 0) { clearInterval(timerInterval); alert("Session Expired."); location.href = "/"; }
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
        if(!selectedRole || selectedAmount === 0) return alert("Select Role & Tier!");
        const u = prompt("ADMIN?");
        const fd = new FormData();
        fd.append("amount", selectedAmount);
        fd.append("awb", document.getElementById("awbField").value || "AUDIT");
        if(u) { fd.append("user", u); fd.append("password", prompt("PASS?")); }
        const res = await fetch("/create-payment", { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<strong>⚙️ ANALYZING STEP-BY-STEP...</strong>";
        const fd = new FormData();
        fd.append("prompt", `I am the ${selectedRole}. Issue: ${document.getElementById("promptArea").value}`);
        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();
        out.innerHTML = `<div class="report">${data.data}</div>`;
    };
});
