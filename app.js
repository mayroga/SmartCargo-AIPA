let imgB64 = ["", "", ""];
let role = "";
let consultInfo = { momento: "", queVe: "" };
let chatHistory = "";

const i18n = {
    en: {
        legal: "SMARTCARGO ADVISORY by May Roga LLC | INDEPENDENT PRIVATE ADVISORY. NOT IATA, DOT, TSA, OR CBP. ALL RESPONSES ARE STRATEGIC SUGGESTIONS ONLY.",
        promoGold: "360° STRATEGIC LOGISTICS SOLUTIONS - SMARTCARGO ADVISORY BY MAY ROGA LLC",
        promoBlue: "MITIGATING HOLDS, RETURNS, SAVING MONEY. WE THINK AND WORK ON YOUR CARGO.",
        capture: " GIVE ME THE DOC",
        get: "EXECUTE ADVISORY",
        prompt: "Tell me what you see, I'm listening...",
        analyzing: "SMARTCARGO ADVISORY by May Roga LLC | ANALYZING STRATEGY...",
        askMomento: "When is this happening? \n1. Starting \n2. Problem \n3. Post",
        askQueVe: "What do you have? \n1. Papers \n2. Cargo \n3. Authority \n4. Not sure",
        roleAlert: "Please select your role",
        clear: "NEW SESSION",
        u: "Username", p: "Password", roles: ["Driver", "Agent", "Warehouse", "Owner"]
    },
    es: {
        legal: "SMARTCARGO ADVISORY by May Roga LLC | ASESORÍA PRIVADA INDEPENDIENTE. NO SOMOS IATA, DOT, TSA O CBP. TODAS LAS RESPUESTAS SON SUGERENCIAS ESTRATÉGICAS.",
        promoGold: "SOLUCIONES LOGÍSTICAS ESTRATÉGICAS 360° - SMARTCARGO ADVISORY BY MAY ROGA LLC",
        promoBlue: "MITIGAMOS RETENCIONES, RETORNOS, AHORRAMOS DINERO. PENSAMOS Y TRABAJAMOS EN TU MERCANCÍA.",
        capture: " MÁNDAME EL DOC",
        get: "RECIBIR ASESORÍA",
        prompt: "Dime qué tienes ahí, te escucho...",
        analyzing: "SMARTCARGO ADVISORY by May Roga LLC | ANALIZANDO ESTRATEGIA...",
        askMomento: "¿Cuándo pasa esto? \n1. Inicio \n2. Problema \n3. Ya pasó",
        askQueVe: "¿Qué tienes? \n1. Papeles \n2. Carga \n3. Autoridad \n4. No sé",
        roleAlert: "Por favor selecciona tu rol",
        clear: "NUEVA CONSULTA",
        u: "Usuario", p: "Clave", roles: ["Chofer", "Agente", "Bodega", "Dueño"]
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
    document.getElementById('promoGold').innerHTML = `<span>${lang.promoGold}</span>`;
    document.getElementById('promoBlue').innerHTML = `<span>${lang.promoBlue}</span>`;
    document.getElementById('btn-get').innerText = lang.get;
    document.getElementById('prompt').placeholder = lang.prompt;
    document.getElementById('btn-clear').innerText = lang.clear;
    document.getElementById('u').placeholder = lang.u;
    document.getElementById('p').placeholder = lang.p;
    for (let i = 1; i <= 3; i++) document.getElementById('txt-capture' + i).innerText = lang.capture;
    for (let i = 1; i <= 4; i++) document.getElementById('role' + i).innerText = lang.roles[i - 1];
}

function scRead(e, n) {
    const r = new FileReader();
    r.onload = () => {
        imgB64[n - 1] = r.result;
        const img = document.getElementById('v' + n);
        img.src = r.result; img.style.display = "block";
        document.getElementById('txt-capture' + n).style.display = "none";
    };
    r.readAsDataURL(e.target.files[0]);
}

function selRole(r, el) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
}

function activarVoz() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) return;
    const rec = new Speech();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    rec.start();
    rec.onresult = (e) => { document.getElementById('prompt').value = e.results[0][0].transcript; };
}

function escuchar() {
    const text = document.getElementById('res').innerText;
    if (!text) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

function limpiar() { location.href = "/"; }

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
    out.style.display = "block";
    out.innerText = i18n[l].analyzing;

    const fd = new FormData();
    fd.append("prompt", `Role: ${role}. Stage: ${consultInfo.momento}. Input: ${document.getElementById('prompt').value}`);
    fd.append("lang", l);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
    } catch (e) { out.innerText = "Error."; }
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
