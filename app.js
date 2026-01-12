let imgB64 = ["", "", ""];
let role = "";
let consultInfo = { momento: "", queVe: "" };
let chatHistory = "";

const i18n = {
    en: {
        legal: "SMARTCARGO ADVISORY by May Roga LLC | INDEPENDENT PRIVATE ADVISORY. NOT IATA, DOT, TSA, OR CBP. ALL RESPONSES ARE STRATEGIC SUGGESTIONS ONLY.",
        promoGold: "360° STRATEGIC LOGISTICS SOLUTIONS - SMARTCARGO ADVISORY BY MAY ROGA LLC",
        promoBlue: "MITIGATING HOLDS, RETURNS, SAVING MONEY. WE THINK AND WORK ON YOUR CARGO.",
        capture: " SCAN DOC ",
        get: "EXECUTE ADVISORY",
        prompt: "Tell me what you see, I'm listening...",
        analyzing: "SMARTCARGO ADVISORY | ANALYZING STANDARDS...",
        askMomento: "Status? \n1. Starting \n2. Problem now \n3. Post-Incident",
        askQueVe: "Evidence? \n1. Papers \n2. Cargo \n3. Officer \n4. Unknown",
        roleAlert: "Please select your role",
        clear: "NEW SESSION",
        u: "User", p: "Pass", roles: ["Trucker", "Forwarder", "Counter", "Shipper"]
    },
    es: {
        legal: "SMARTCARGO ADVISORY by May Roga LLC | ASESORÍA PRIVADA INDEPENDIENTE. NO SOMOS IATA, DOT, TSA O CBP. TODAS LAS RESPUESTAS SON SUGERENCIAS ESTRATÉGICAS.",
        promoGold: "SOLUCIONES LOGÍSTICAS ESTRATÉGICAS 360° - SMARTCARGO ADVISORY BY MAY ROGA LLC",
        promoBlue: "MITIGAMOS RETENCIONES, RETORNOS, AHORRAMOS DINERO. PENSAMOS Y TRABAJAMOS EN TU MERCANCÍA.",
        capture: " ESCANEAR DOC ",
        get: "RECIBIR ASESORÍA",
        prompt: "Dime qué ves, te escucho para asesorarte...",
        analyzing: "SMARTCARGO ADVISORY | ANALIZANDO ESTÁNDARES...",
        askMomento: "¿Estado? \n1. Empezando \n2. Problema ahora \n3. Post-incidente",
        askQueVe: "¿Qué tienes a la mano? \n1. Papeles \n2. Carga \n3. Autoridad \n4. No sé",
        roleAlert: "Por favor selecciona tu rol",
        clear: "NUEVA CONSULTA",
        u: "Usuario", p: "Clave", roles: ["Camionero", "Forwarder", "Counter", "Dueño/Shipper"]
    }
};

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('txt-legal').innerText = lang.legal;
    document.getElementById('promoGold').innerHTML = `<span>${lang.promoGold}</span>`;
    document.getElementById('promoBlue').innerHTML = `<span>${lang.promoBlue}</span>`;
    document.getElementById('btn-get').innerText = lang.get;
    document.getElementById('prompt').placeholder = lang.prompt;
    document.getElementById('btn-clear').innerText = lang.clear;
    const roleBtns = document.querySelectorAll('.role-btn');
    roleBtns.forEach((btn, idx) => { if(idx < lang.roles.length) btn.innerText = lang.roles[idx]; });
}

// MICROPHONE - PUSH TO TALK
let recognition;
function startVoice() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) return;
    recognition = new Speech();
    recognition.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    recognition.continuous = true;
    recognition.onresult = (e) => {
        document.getElementById('prompt').value = e.results[e.results.length - 1][0].transcript;
    };
    recognition.start();
}
function stopVoice() { if(recognition) recognition.stop(); }

function escuchar() {
    let text = document.getElementById('res').innerText;
    if (!text || text.includes("...")) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

function imprimirPDF() {
    const content = document.getElementById('res').innerText;
    const v = window.open('', '', 'height=700,width=900');
    v.document.write('<html><body><h1>SmartCargo Advisory Report</h1><pre>' + content + '</pre></body></html>');
    v.document.close(); v.print();
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("Copied"); }
function enviarEmail() { window.open("mailto:?subject=SmartCargo Advisory Report&body=" + encodeURIComponent(document.getElementById('res').innerText)); }

function limpiar() {
    document.getElementById('prompt').value = "";
    document.getElementById('res').style.display = "none";
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    role = "";
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
    out.style.display = "block"; out.innerText = i18n[l].analyzing;
    const fd = new FormData();
    fd.append("prompt", document.getElementById('prompt').value);
    fd.append("role", role);
    fd.append("lang", l);
    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
    } catch (e) { out.innerText = "Error."; }
}

function selRole(r, el) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
}

function scRead(e, n) {
    const r = new FileReader();
    r.onload = () => {
        imgB64[n - 1] = r.result;
        document.getElementById('v' + n).src = r.result;
        document.getElementById('v' + n).style.display = "block";
        document.getElementById('txt-capture' + n).style.display = "none";
    };
    r.readAsDataURL(e.target.files[0]);
}
