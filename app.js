let role = "";
let chatHistory = "";

const i18n = {
    en: { get: "EXECUTE ADVISORY", roles: ["Trucker", "Forwarder", "Counter Staff", "Shipper/Owner"] },
    es: { get: "EJECUTAR ASESORÍA", roles: ["Camionero", "Forwarder", "Agente Counter", "Dueño/Shipper"] }
};

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('btn-get').innerText = lang.get;
    document.querySelectorAll('.role-btn').forEach((b, i) => b.innerText = lang.roles[i]);
}

function hablar(t) {
    window.speechSynthesis.cancel();
    const cleanText = t.replace(/[*#_]/g, "").replace(/-/g, " ");
    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

async function run() {
    if (!role) return alert("Select Role / Selecciona Rol");
    const p = document.getElementById('prompt').value;
    const out = document.getElementById('res');
    out.style.display = "block"; 
    out.innerText = "SMARTCARGO ADVISORY by MAY ROGA LLC | Analyzing...";

    const fd = new FormData();
    fd.append("prompt", `HISTORY: ${chatHistory} | NEW: ${p}`);
    fd.append("role", role);
    fd.append("lang", document.getElementById('userLang').value);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        if (!r.ok) throw new Error();
        const d = await r.json();
        out.innerText = d.data;
        document.getElementById('speak-btn').style.display = "block";
        chatHistory += ` Q:${p} A:${d.data} | `;
    } catch (e) {
        out.innerText = "CONNECTION ERROR. Verify your internet or API Keys.";
    }
}

// CORRECCIÓN DEFINITIVA BOTÓN CORREO
function email() {
    const text = document.getElementById('res').innerText;
    const subject = "SMARTCARGO ADVISORY by MAY ROGA LLC - Report";
    const mailtoLink = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(text)}`;
    
    // Crear un link invisible y clickearlo para evitar bloqueos
    const tempLink = document.createElement('a');
    tempLink.href = mailtoLink;
    tempLink.click();
}

function ws() {
    const text = document.getElementById('res').innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}

function selRole(r, b) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
}

// Mantenemos el resto de funciones igual (startVoice, stopVoice, pay, etc.)
let rec;
function startVoice() {
    const S = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!S) return;
    rec = new S();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    rec.onresult = (e) => document.getElementById('prompt').value = e.results[0][0].transcript;
    rec.start();
}
function stopVoice() { if(rec) rec.stop(); }

const params = new URLSearchParams(window.location.search);
if (params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = "none";
    document.getElementById('mainApp').style.display = "block";
}
