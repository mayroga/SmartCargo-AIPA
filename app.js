let selectedRole = "", selectedAmount = 0, timeLeft = 0;

function selRole(v, el) { 
    selectedRole = v; 
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); 
    el.classList.add('selected'); 
}

function selTier(v, el) { 
    selectedAmount = v; 
    document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected')); 
    el.classList.add('selected'); 
}

function loadPhoto(i) {
    const file = document.getElementById(`f${i}`).files[0];
    if (file) {
        const r = new FileReader();
        r.onload = (e) => { document.getElementById(`p${i}`).src = e.target.result; };
        r.readAsDataURL(file);
    }
}

async function getSolution() {
    const out = document.getElementById("advResponse");
    out.innerText = "Processing...";
    const fd = new FormData();
    fd.append("prompt", `Role: ${selectedRole}. Issue: ${document.getElementById("promptArea").value}`);
    try {
        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();
        out.innerText = data.data;
        document.getElementById("btnWs").style.display = "block";
    } catch(e) { out.innerText = "Error. Try again."; }
}

document.getElementById("activateBtn").onclick = async () => {
    if(!selectedRole || selectedAmount === 0) return alert("Select Role and Price");
    const awb = document.getElementById("awbField").value || "N/A";
    const fd = new FormData();
    fd.append("amount", selectedAmount);
    fd.append("awb", awb);
    
    const u = prompt("Admin User? (Leave blank for Card Payment)");
    if(u) {
        fd.append("user", u);
        fd.append("password", prompt("Admin Pass?"));
    }

    const res = await fetch("/create-payment", { method: "POST", body: fd });
    const data = await res.json();
    if(data.url) window.location.href = data.url; else alert("Check Admin credentials or Internet.");
};

document.addEventListener("DOMContentLoaded", () => {
    const p = new URLSearchParams(window.location.search);
    if(p.get("access") === "granted") {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        const t = p.get("tier");
        timeLeft = (t == 95 ? 45 : (t == 35 ? 20 : (t == 15 ? 10 : 4))) * 60;
        setInterval(() => {
            timeLeft--;
            document.getElementById("timerDisp").innerText = `ACTIVE SESSION: ${Math.floor(timeLeft/60)}m ${timeLeft%60}s`;
            if(timeLeft <= 0) window.location.href = "/";
        }, 1000);
    }
});

function sendWS() { window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(document.getElementById("advResponse").innerText)}`); }

// Función para borrar el texto y la respuesta previa
function clearText() {
    if(confirm("¿Borrar descripción y respuesta actual?")) {
        document.getElementById("promptArea").value = "";
        document.getElementById("advResponse").innerText = "";
        document.getElementById("btnWs").style.display = "none";
        // Limpiar fotos
        for(let i=1; i<=3; i++) {
            document.getElementById(`p${i}`).src = "";
            document.getElementById(`f${i}`).value = "";
        }
    }
}

// Función de voz optimizada
function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Tu navegador no soporta reconocimiento de voz.");
        return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES'; 
    
    const area = document.getElementById("promptArea");
    const originalPlaceholder = area.placeholder;
    area.placeholder = "Listening / Escuchando...";

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        area.value += (area.value ? " " : "") + transcript;
        area.placeholder = originalPlaceholder;
    };

    recognition.onerror = () => {
        area.placeholder = originalPlaceholder;
    };

    recognition.start();
}
