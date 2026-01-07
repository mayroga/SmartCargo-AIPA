let imgB64 = ""; let role = ""; let timeLeft = 0;

const i18n = {
    en: {
        legal: "PRIVATE ADVISORY. NOT IATA, TSA, DOT. NOT GOVERNMENT.",
        capture: "📷 CAPTURE CARGO / DOCS",
        get: "GET TECHNICAL SOLUTION",
        master: "MASTER ACCESS",
        clear: "CLEAR CONSULT",
        prompt: "Describe your case or use Microphone...",
        analyzing: "Analyzing cargo data...",
        timer: "TIME:"
    },
    es: {
        legal: "ASESORÍA PRIVADA. NO SOMOS IATA, TSA, DOT. NO GOBIERNO.",
        capture: "📷 CAPTURAR CARGA / DOCS",
        get: "OBTENER SOLUCIÓN TÉCNICA",
        master: "ACCESO MAESTRO",
        clear: "LIMPIAR CONSULTA",
        prompt: "Describa su caso o use el Micrófono...",
        analyzing: "Analizando datos de carga...",
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
    const tDiv = document.getElementById('timer');
    if(tDiv.style.display === "block") {
        let current = tDiv.innerText.split(" ")[1];
        tDiv.innerText = `${i18n[l].timer} ${current}`;
    }
}

const params = new URLSearchParams(window.location.search);
if(params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    const t = {"5":300, "15":900, "35":1800, "95":3600, "0":86400};
    timeLeft = t[params.get('monto')] || 300;
    const tDiv = document.getElementById('timer'); tDiv.style.display = "block";
    setInterval(() => {
        if(timeLeft <= 0) {
            alert("Session Expired");
            location.href = "/";
        }
        let m = Math.floor(timeLeft / 60); let s = timeLeft % 60;
        let lang = document.getElementById('userLang').value;
        tDiv.innerText = `${i18n[lang].timer} ${m}:${s<10?'0':''}${s}`;
        timeLeft--;
    }, 1000);
}

// NUEVA FUNCIÓN DE PRE-ESCÁNER
async function preScanVision() {
    if(!imgB64) return;
    const fd = new FormData();
    fd.append("image_data", imgB64);
    fd.append("lang", document.getElementById('userLang').value);

    try {
        const r = await fetch("/vision-scan", {
            method: "POST",
            body: fd
        });
        const d = await r.json();

        if(d.description) {
            const p = document.getElementById('prompt');
            // Se inyecta la descripción visual al principio sin borrar lo que el usuario escribió
            p.value = "AUTO VISUAL SCAN:\n" + d.description + "\n\n" + (p.value || "");
        }
    } catch(e) {
        console.warn("Vision pre-scan skipped");
    }
}

function scRead(e) {
    const r = new FileReader();
    r.onload = () => { 
        imgB64 = r.result; 
        document.getElementById('v').src = imgB64; 
        document.getElementById('v').style.display="block"; 
        document.getElementById('txt-capture').style.display="none"; 

        // 🔥 LÍNEA NUEVA: Dispara el análisis visual en cuanto sube la foto
        preScanVision();
    };
    r.readAsDataURL(e.target.files[0]);
}

function activarVoz() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!Speech) return alert("Voz no soportada en este navegador");
    const rec = new Speech();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-ES' : 'en-US';
    rec.start();
    rec.onresult = (e) => { document.getElementById('prompt').value = e.results[0][0].transcript; };
}

async function pay(amt) {
    const fd = new FormData(); 
    fd.append("amount", amt); 
    fd.append("awb", document.getElementById('awb').value || "REF");
    fd.append("user", document.getElementById('u').value); 
    fd.append("password", document.getElementById('p').value);
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json(); 
    if(d.url) window.location.href = d.url;
    else alert("Access Denied");
}

async function run() {
    if(!role) return alert("Please select your Role (Shipper, Forwarder, etc.)");
    const out = document.getElementById('res'); 
    const lang = document.getElementById('userLang').value;
    out.style.display = "block"; 
    out.innerText = i18n[lang].analyzing;
    
    const fd = new FormData();
    fd.append("prompt", `Role: ${role}. Case: ${document.getElementById('prompt').value || "Visual inspection requested."}`);
    fd.append("lang", lang);
    if(imgB64) fd.append("image_data", imgB64);
    
    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json(); 
        if(d.image) {
            document.getElementById('v').src = d.image;
        }
        out.innerText = d.data || "SYSTEM: Error in response structure.";
    } catch(e) { 
        console.error(e);
        out.innerText = "Connection Error. Please describe your cargo via text or voice."; 
    }
}

function limpiar() {
    imgB64 = ""; 
    document.getElementById('v').style.display="none"; 
    document.getElementById('txt-capture').style.display="block";
    document.getElementById('prompt').value = ""; 
    document.getElementById('res').innerText = "";
    document.getElementById('res').style.display = "none";
}

function selRole(r, el) { 
    role = r; 
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected')); 
    el.classList.add('selected'); 
}

function ws() { 
    const text = document.getElementById('res').innerText;
    window.open("https://wa.me/?text=" + encodeURIComponent(text)); 
}

function copy() { 
    const text = document.getElementById('res').innerText;
    navigator.clipboard.writeText(text); 
    alert("Copied to clipboard"); 
}
