let role = "";
let chatHistory = "";

window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('access') === 'granted') {
        document.getElementById('accessSection').style.display = "none";
        document.getElementById('mainApp').style.display = "block";
    }
});

function selRole(r, el) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
}

// --- VOZ ---
function activarVoz() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) return alert("Navegador no compatible.");
    const rec = new Speech();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    rec.start();
    rec.onresult = (e) => { document.getElementById('prompt').value = e.results[0][0].transcript; };
}

function escucharRespuesta() {
    const text = document.getElementById('res').innerText;
    if (!text) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

// --- ACCIÓN ---
async function run() {
    const l = document.getElementById('userLang').value;
    if (!role) return alert("Seleccione su Rol.");
    const out = document.getElementById('res');
    const input = document.getElementById('prompt').value;
    if (!input) return;

    out.style.display = "block";
    out.innerText = "CEREBRO SMARTCARGO PROCESANDO...";

    const fd = new FormData();
    fd.append("prompt", input);
    fd.append("lang", l);
    fd.append("role", role);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        document.getElementById('voice-out').style.display = 'block';
    } catch (e) { out.innerText = "Error de conexión."; }
}

// --- SALIDAS ---
function imprimirResultado() {
    const contenido = document.getElementById('res').innerText;
    const v = window.open('', '', 'height=700,width=900');
    v.document.write('<html><head><title>SmartCargo Report</title><style>body{font-family:sans-serif;padding:40px;}.header{text-align:center;border-bottom:3px solid #d4af37;}pre{white-space:pre-wrap;background:#f4f4f4;padding:20px;}</style></head><body>');
    v.document.write('<div class="header"><h1>SMARTCARGO ADVISORY</h1><p>MAY ROGA LLC</p></div>');
    v.document.write('<pre>' + contenido + '</pre></body></html>');
    v.document.close();
    v.print();
}

function copyToClipboard() {
    navigator.clipboard.writeText(document.getElementById('res').innerText);
    alert("Copiado al portapapeles.");
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function limpiar() { location.href = "/"; }

async function pay(amt) {
    const awb = document.getElementById('awb').value || "REF";
    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", awb);
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.url) window.location.href = d.url;
}
