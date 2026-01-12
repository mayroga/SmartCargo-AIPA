let role = "";
let chatHistory = "";

const i18n = {
    en: { get: "EXECUTE ADVISORY", roles: ["Trucker", "Forwarder", "Counter Staff", "Shipper/Owner"], analyzing: "SMARTCARGO ADVISORY | ANALYZING..." },
    es: { get: "EJECUTAR ASESORÍA", roles: ["Camionero", "Forwarder", "Agente Counter", "Dueño/Shipper"], analyzing: "SMARTCARGO ADVISORY | ANALIZANDO..." }
};

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('btn-get').innerText = lang.get;
    document.querySelectorAll('.role-btn').forEach((b, i) => b.innerText = lang.roles[i]);
}

// CÁMARAS
function scRead(e, n) {
    const r = new FileReader();
    r.onload = () => {
        const img = document.getElementById('v' + n);
        img.src = r.result; img.style.display = "block";
        document.getElementById('cap' + n).style.display = "none";
    };
    r.readAsDataURL(e.target.files[0]);
}

// BOCINA (Speaker)
function hablar(t) {
    window.speechSynthesis.cancel();
    const cleanText = t.replace(/🔊/g, "").replace(/[*#_]/g, "").replace(/-/g, " ");
    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

// MICRÓFONO (Dictado)
let rec;
function startVoice() {
    const S = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!S) return alert("Microphone not supported.");
    rec = new S();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    rec.onresult = (e) => document.getElementById('prompt').value = e.results[0][0].transcript;
    rec.start();
}
function stopVoice() { if(rec) rec.stop(); }

// PAGOS Y ACCESO
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

// EJECUCIÓN DE IA (REPARADA)
async function run() {
    if (!role) return alert("Select Role / Selecciona Rol");
    const p = document.getElementById('prompt').value;
    const out = document.getElementById('res');
    const lang = document.getElementById('userLang').value;
    
    out.style.display = "block";
    out.innerText = i18n[lang].analyzing;
    document.getElementById('speak-btn').style.display = "none";

    const fd = new FormData();
    fd.append("prompt", `HISTORY: ${chatHistory} | QUERY: ${p}`);
    fd.append("role", role);
    fd.append("lang", lang);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        if (!r.ok) throw new Error("Server Error");
        const d = await r.json();
        
        out.innerText = d.data;
        document.getElementById('speak-btn').style.display = "block";
        chatHistory += ` Q:${p} A:${d.data} | `;
    } catch (e) {
        out.innerText = "CONNECTION ERROR: The IA brain is not responding. Check Render Logs.";
    }
}

function selRole(r, b) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
}

// EXPORTACIÓN
function ws() {
    const text = document.getElementById('res').innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}
function email() {
    const text = document.getElementById('res').innerText;
    const subject = "SMARTCARGO ADVISORY REPORT";
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(text)}`;
}

// DETECCIÓN DE ACCESO
const params = new URLSearchParams(window.location.search);
if (params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = "none";
    document.getElementById('mainApp').style.display = "block";
}
