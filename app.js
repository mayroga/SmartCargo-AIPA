let imgB64 = ["", "", ""];
let role = "";
let consultInfo = { momento: "", queVe: "" };
let chatHistory = "";

const i18n = {
    en: {
        legal: "PRIVATE ADVISORY. NOT GOV. TOTAL KNOWLEDGE.",
        capture: "📷 SEND DOC / PHOTO",
        get: "GET SOLUTION",
        prompt: "Tell me what you see, I'm listening...",
        analyzing: "MAY ROGA LLC | SOLVING NOW...",
        askMomento: "When is this? 1.Starting 2.Issue now 3.Already happened",
        askQueVe: "What's in your hand? 1.Papers 2.Cargo 3.Authority 4.Not sure",
        roleAlert: "Select your Role",
        clear: "NEW CONSULT"
    },
    es: {
        legal: "ASESORÍA PRIVADA. NO SOMOS IATA, DOT, TSA O CBP. NO GOBIERNO.",
        capture: "📷 MÁNDAME EL DOC / FOTO",
        get: "RECIBIR ASESORÍA",
        prompt: "Dime qué tienes ahí, te escucho...",
        analyzing: "MAY ROGA LLC | RESOLVIENDO YA...",
        askMomento: "¿Cuándo pasa esto? 1.Empezando 2.Problema ahora 3.Ya pasó",
        askQueVe: "¿Qué tienes en la mano? 1.Papeles 2.Carga 3.Autoridad 4.No sé",
        roleAlert: "Selecciona tu Rol",
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
    chatHistory = "";
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
    if (!consultInfo.momento) consultInfo.momento = prompt(i18n[l].askMomento) || "N/A";
    if (!consultInfo.queVe) consultInfo.queVe = prompt(i18n[l].askQueVe) || "N/A";
    run();
}

async function run() {
    const l = document.getElementById('userLang').value;
    if (!role) return alert(i18n[l].roleAlert);
    const out = document.getElementById('res');
    const userInput = document.getElementById('prompt').value || "Check";
    out.style.display = "block";
    out.innerText = i18n[l].analyzing;

    const fd = new FormData();
    fd.append("prompt", `HISTORY: ${chatHistory}. CURRENT_PROBLEM: ${userInput}. Role: ${role}. Stage: ${consultInfo.momento}. Observations: ${consultInfo.queVe}`);
    fd.append("lang", l);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        chatHistory += ` | User: ${userInput} | Advisor: ${d.data}`; 
    } catch (e) { out.innerText = "Error de conexión."; }
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
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("OK"); }

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
