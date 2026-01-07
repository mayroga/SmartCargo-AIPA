let imgB64 = ""; let role = ""; let timeLeft = 0;

const i18n = {
    en: {
        legal: "PRIVATE ADVISORY. NOT IATA, TSA, DOT. NOT GOVERNMENT.",
        capture: "📷 CAPTURE CARGO / DOCS",
        get: "GET TECHNICAL SOLUTION",
        master: "MASTER ACCESS",
        clear: "CLEAR CONSULT",
        prompt: "Describe your case or use Microphone...",
        analyzing: "Analyzing data...",
        timer: "TIME:"
    },
    es: {
        legal: "ASESORÍA PRIVADA. NO SOMOS IATA, TSA, DOT. NO GOBIERNO.",
        capture: "📷 CAPTURAR CARGA / DOCS",
        get: "OBTENER SOLUCIÓN TÉCNICA",
        master: "ACCESO MAESTRO",
        clear: "LIMPIAR CONSULTA",
        prompt: "Describa su caso o use el Micrófono...",
        analyzing: "Analizando datos...",
        timer: "TIEMPO:"
    }
};

function changeLang(l) {
    document.getElementById('txt-legal').innerText = i18n[l].legal;
    document.getElementById('txt-capture').innerText = i18n[l].capture;
    document.getElementById('txt-get').innerText = i18n[l].get;
    if(document.getElementById('txt-master')) document.getElementById('txt-master').innerText = i18n[l].master;
    document.getElementById('txt-clear').innerText = i18n[l].clear;
    document.getElementById('prompt').placeholder = i18n[l].prompt;
}

const params = new URLSearchParams(window.location.search);
if(params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    const t = {"5":300, "15":900, "35":1800, "95":3600, "0":86400};
    timeLeft = t[params.get('monto')] || 300;
    const tDiv = document.getElementById('timer'); tDiv.style.display = "block";
    setInterval(() => {
        if(timeLeft <= 0) location.href = "/";
        let m = Math.floor(timeLeft / 60); let s = timeLeft % 60;
        tDiv.innerText = `${i18n[document.getElementById('userLang').value].timer} ${m}:${s<10?'0':''}${s}`;
        timeLeft--;
    }, 1000);
}

function scRead(e) {
    const r = new FileReader();
    r.onload = () => { imgB64 = r.result; document.getElementById('v').src = imgB64; document.getElementById('v').style.display="block"; document.getElementById('txt-capture').style.display="none"; };
    r.readAsDataURL(e.target.files[0]);
}

function activarVoz() {
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-ES' : 'en-US';
    rec.start();
    rec.onresult = (e) => { document.getElementById('prompt').value = e.results[0][0].transcript; };
}

async function pay(amt) {
    const fd = new FormData(); fd.append("amount", amt); fd.append("awb", document.getElementById('awb').value || "REF");
    fd.append("user", document.getElementById('u').value); fd.append("password", document.getElementById('p').value);
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json(); if(d.url) window.location.href = d.url;
}

async function run() {
    if(!role) return alert("Select Role");
    const out = document.getElementById('res'); out.style.display = "block"; 
    out.innerText = i18n[document.getElementById('userLang').value].analyzing;
    const fd = new FormData();
    fd.append("prompt", `Role: ${role}. Case: ${document.getElementById('prompt').value}`);
    fd.append("lang", document.getElementById('userLang').value);
    if(imgB64) fd.append("image_data", imgB64);
    const r = await fetch('/advisory', { method: 'POST', body: fd });
    const d = await r.json(); out.innerText = d.data;
}

function limpiar() {
    imgB64 = ""; document.getElementById('v').style.display="none"; 
    document.getElementById('txt-capture').style.display="block";
    document.getElementById('prompt').value = ""; document.getElementById('res').innerText = "";
}

function selRole(r, el) { role = r; document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }
function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("Copied"); }
