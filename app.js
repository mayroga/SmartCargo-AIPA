let imgB64 = ["", "", ""];
let role = "";
let consultInfo = { momento: "", queVe: "" };

const i18n = {
    en: {
        legal: "PRIVATE ADVISORY. NOT GOV. TOTAL KNOWLEDGE.",
        capture: "📷 PHOTO / DOCUMENT",
        get: "GET SOLUTION",
        prompt: "Tell me what happened or what you see...",
        analyzing: "MAY ROGA LLC | PROCESSING SOLUTION...",
        askMomento: "When is this happening? (1.Planning, 2.Now/Problem, 3.Already happened)",
        askQueVe: "What's in front of you? (1.Papers, 2.Things/Boxes, 3.People/Police, 4.Not sure)",
        roleAlert: "Please select your Role",
        clear: "NEW CONSULT"
    },
    es: {
        legal: "ASESORÍA PRIVADA. NO GOBIERNO. CONOCIMIENTO TOTAL.",
        capture: "📷 FOTO / DOCUMENTO",
        get: "OBTENER SOLUCIÓN",
        prompt: "Dime qué pasó o qué estás viendo...",
        analyzing: "MAY ROGA LLC | PROCESANDO SOLUCIÓN...",
        askMomento: "¿Cuándo está pasando esto? (1.Planeando, 2.Ahora/Problema, 3.Ya pasó)",
        askQueVe: "¿Qué tienes enfrente? (1.Papeles, 2.Cosas/Cajas, 3.Personas/Policía, 4.No sé)",
        roleAlert: "Por favor selecciona tu Rol",
        clear: "NUEVA CONSULTA"
    }
};

window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('access') === 'granted') {
        document.getElementById('accessSection').style.display = "none";
        document.getElementById('mainApp').style.display = "block";
    }
});

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('txt-legal').innerText = lang.legal;
    document.getElementById('btn-get').innerText = lang.get;
    document.getElementById('prompt').placeholder = lang.prompt;
    document.getElementById('btn-clear').innerText = lang.clear;
    for (let i = 1; i <= 3; i++) {
        const span = document.getElementById('txt-capture' + i);
        if (span) span.innerText = lang.capture;
    }
}

function scRead(e, n) {
    const r = new FileReader();
    r.onload = () => {
        imgB64[n - 1] = r.result;
        const img = document.getElementById('v' + n);
        img.src = r.result;
        img.style.display = "block";
        document.getElementById('txt-capture' + n).style.display = "none";
    };
    r.readAsDataURL(e.target.files[0]);
}

function limpiar() {
    imgB64 = ["", "", ""];
    for (let i = 1; i <= 3; i++) {
        const img = document.getElementById('v' + i);
        const txt = document.getElementById('txt-capture' + i);
        if (img) { img.src = ""; img.style.display = "none"; }
        if (txt) txt.style.display = "block";
    }
    document.getElementById('prompt').value = "";
    document.getElementById('res').innerText = "";
    document.getElementById('res').style.display = "none";
    consultInfo = { momento: "", queVe: "" };
    role = "";
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
}

function selRole(r, el) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
}

async function preRun() {
    const l = document.getElementById('userLang').value;
    const langData = i18n[l];
    // Se eliminó la restricción de "return". Si le da OK en blanco, el proceso sigue.
    if (!consultInfo.momento) consultInfo.momento = prompt(langData.askMomento) || "Not specified";
    if (!consultInfo.queVe) consultInfo.queVe = prompt(langData.askQueVe) || "Not specified";
    run();
}

async function run() {
    const l = document.getElementById('userLang').value;
    if (!role) return alert(i18n[l].roleAlert);
    const out = document.getElementById('res');
    out.style.display = "block";
    out.innerText = i18n[l].analyzing;
    const fd = new FormData();
    fd.append("prompt", `Stage: ${consultInfo.momento}. Focus: ${consultInfo.queVe}. Role: ${role}. Input: ${document.getElementById('prompt').value || "None"}`);
    fd.append("lang", l);
    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
    } catch (e) { out.innerText = "Error."; }
}

function activarVoz() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) return;
    const rec = new Speech();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-ES' : 'en-US';
    rec.start();
    rec.onresult = (e) => { document.getElementById('prompt').value = e.results[0][0].transcript; };
}

function escuchar() {
    const text = document.getElementById('res').innerText;
    if (!text || text.includes("...")) return;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-ES' : 'en-US';
    window.speechSynthesis.speak(utter);
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); }

async function pay(amt) {
    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", document.getElementById('awb').value || "REF");
    fd.append("user", document.getElementById('u').value);
    fd.append("password", document.getElementById('p').value);
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.url) window.location.href = d.url;
}
