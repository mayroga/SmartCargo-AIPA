let role = "";
let chatHistory = "";

const i18n = {
    en: { get: "EXECUTE ADVISORY", new: "NEW CONSULTATION", roles: ["Trucker", "Forwarder", "Counter Staff", "Shipper/Owner"] },
    es: { get: "EJECUTAR ASESORÍA", new: "NUEVA CONSULTA", roles: ["Camionero", "Forwarder", "Agente Counter", "Dueño/Shipper"] }
};

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('btn-get').innerText = lang.get;
    document.getElementById('btn-new').innerText = lang.new;
    document.querySelectorAll('.role-btn').forEach((b, i) => b.innerText = lang.roles[i]);
}

function hablar(t) {
    window.speechSynthesis.cancel();
    const cleanText = t.replace(/🔊/g, "").replace(/[*#_]/g, "").replace(/-/g, " ");
    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

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

async function pay(amt) {
    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", document.getElementById('awb').value || "REF");
    fd.append("user", document.getElementById('u').value);
    fd.append("p", document.getElementById('p').value);
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.url) window.location.href = d.url;
}

async function run() {
    if (!role) return alert("Select Role / Selecciona Rol");
    const p = document.getElementById('prompt').value;
    const out = document.getElementById('res');
    out.style.display = "block"; out.innerText = "Analyzing...";
    document.getElementById('speak-btn').style.display = "none";

    const fd = new FormData();
    fd.append("prompt", `CHAT HISTORY: ${chatHistory} | NEW INQUIRY: ${p}`);
    fd.append("role", role);
    fd.append("lang", document.getElementById('userLang').value);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        document.getElementById('speak-btn').style.display = "block";
        chatHistory += ` User: ${p} AI: ${d.data} | `;
    } catch (e) {
        out.innerText = "CONNECTION ERROR: Check your Render API Keys.";
    }
}

function selRole(r, b) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function email() { window.location.href = `mailto:?subject=SmartCargo Advisory Report&body=${encodeURIComponent(document.getElementById('res').innerText)}`; }

const params = new URLSearchParams(window.location.search);
if (params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = "none";
    document.getElementById('mainApp').style.display = "block";
}
