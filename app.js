let imgB64 = ""; let role = ""; let timeLeft = 0;

// Autopropaganda Dinámica
const ads = ["Prevenimos multas de CBP.","Expertos en IATA y TSA.","Soluciones Antes, Durante y Después.","SmartCargo: Tranquilidad 24/7."];
let i = 0; setInterval(() => { document.getElementById('ad').innerText = ads[i++ % ads.length]; }, 3500);

// Control de Acceso y Reloj
const params = new URLSearchParams(window.location.search);
if(params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    const tiempos = {"5":300, "15":900, "35":1800, "95":3600, "0":86400};
    timeLeft = tiempos[params.get('monto')] || 300;
    const tDiv = document.getElementById('timer');
    tDiv.style.display = "block";
    setInterval(() => {
        if(timeLeft <= 0) location.href = "/";
        let m = Math.floor(timeLeft / 60); let s = timeLeft % 60;
        tDiv.innerText = `TIEMPO RESTANTE: ${m}:${s<10?'0':''}${s}`;
        timeLeft--;
    }, 1000);
}

function selRole(r, el) { role = r; document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); el.classList.add('selected'); }

function scRead(e) {
    const r = new FileReader();
    r.onload = () => { imgB64 = r.result; document.getElementById('v').src = imgB64; document.getElementById('v').style.display="block"; document.getElementById('l').style.display="none"; };
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
    if(!role) return alert("Seleccione Rol.");
    const out = document.getElementById('res'); out.style.display = "block"; out.innerText = "Analizando...";
    const fd = new FormData(); fd.append("prompt", `Rol: ${role}. ${document.getElementById('prompt').value}`);
    fd.append("lang", document.getElementById('userLang').value);
    if(imgB64) fd.append("image_data", imgB64);
    const r = await fetch('/advisory', { method: 'POST', body: fd });
    const d = await r.json(); out.innerText = d.data;
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("Copiado"); }
