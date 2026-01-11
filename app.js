let role = "";
let chatHistory = "";

function selRole(r, el) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
}

// --- FUNCIONES DE VOZ ---
function activarVoz() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) return alert("Su navegador no soporta dictado por voz.");
    const rec = new Speech();
    const l = document.getElementById('userLang').value;
    rec.lang = l === 'es' ? 'es-US' : 'en-US';
    rec.start();
    rec.onresult = (e) => { document.getElementById('prompt').value = e.results[0][0].transcript; };
}

function escucharRespuesta() {
    const text = document.getElementById('res').innerText;
    if (!text || text.includes("...")) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    const l = document.getElementById('userLang').value;
    utter.lang = l === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

// --- LOGICA PRINCIPAL ---
async function run() {
    const l = document.getElementById('userLang').value;
    if (!role) return alert("Seleccione Rol.");
    const out = document.getElementById('res');
    const input = document.getElementById('prompt').value;
    if (!input) return;

    out.style.display = "block";
    out.innerText = "CEREBRO SMARTCARGO ANALIZANDO...";

    const fd = new FormData();
    fd.append("prompt", `Role: ${role}. Input: ${input}. History: ${chatHistory}`);
    fd.append("lang", l);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        chatHistory += ` | User: ${input} | Advisor: ${d.data}`;
    } catch (e) { out.innerText = "Error de conexión."; }
}

// --- SALIDAS PROFESIONALES ---
function imprimirResultado() {
    const contenido = document.getElementById('res').innerText;
    const ventana = window.open('', '', 'height=700,width=900');
    ventana.document.write('<html><head><title>Reporte SmartCargo</title><style>body{font-family:sans-serif;padding:40px;} .header{text-align:center;border-bottom:3px solid #d4af37;} pre{white-space:pre-wrap;background:#f9f9f9;padding:15px;border-left:5px solid #d4af37;}</style></head><body>');
    ventana.document.write('<div class="header"><h1>SMARTCARGO ADVISORY</h1><p>BY MAY ROGA LLC</p></div>');
    ventana.document.write('<pre>' + contenido + '</pre></body></html>');
    ventana.document.close();
    ventana.print();
}

async function enviarEmail() {
    const email = prompt("Email del cliente:");
    if (!email) return;
    const fd = new FormData();
    fd.append("email", email);
    fd.append("content", document.getElementById('res').innerText);
    await fetch('/send-email', { method: 'POST', body: fd });
    alert("Enviado.");
}

function copyToClipboard() {
    const text = document.getElementById('res').innerText;
    navigator.clipboard.writeText(text).then(() => alert("Copiado."));
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function limpiar() { location.reload(); }
