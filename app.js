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
        prompt: "Tell me what you see, I'm listening to suggest the best path...",
        analyzing: "SMARTCARGO ADVISORY by May Roga LLC | ANALYZING STRATEGY...",
        askMomento: "When is this happening? \n1. Just starting \n2. I have a problem now \n3. It already happened",
        askQueVe: "What do you have in your hand? \n1. Papers \n2. Things/Cargo \n3. A person/Officer \n4. Not sure",
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
        prompt: "Dime qué tienes ahí, te escucho para asesorarte...",
        analyzing: "SMARTCARGO ADVISORY by May Roga LLC | ANALIZANDO ESTRATEGIA...",
        askMomento: "¿Cuándo está pasando esto? \n1. Empezando \n2. Problema ahora \n3. Ya pasó el lío",
        askQueVe: "¿Qué tienes a la mano? \n1. Papeles \n2. Carga \n3. Autoridad \n4. No sé",
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
    for (let i = 1; i <= 3; i++) {
        let txt = document.getElementById('txt-capture' + i);
        if (txt && imgB64[i-1] === "") txt.innerText = lang.capture;
    }
    const roleBtns = document.querySelectorAll('.role-btn');
    roleBtns.forEach((btn, idx) => { if(idx < lang.roles.length) btn.innerText = lang.roles[idx]; });
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
    let text = document.getElementById('res').innerText;
    if (!text || text.includes("...")) return;
    // LIMPIEZA DE VOZ HUMANA
    text = text.replace(/[*#\\_]/g, "").replace(/\[.*?\]/g, "").replace(/-/g, " "); 
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    utter.rate = 0.95; 
    window.speechSynthesis.speak(utter);
}

function imprimirPDF() {
    const contenido = document.getElementById('res').innerText;
    if (!contenido) return;
    const v = window.open('', '', 'height=700,width=900');
    v.document.write('<html><head><title>SmartCargo Report</title><style>body{font-family:sans-serif;padding:40px;line-height:1.6;}pre{white-space:pre-wrap;background:#f0f7ff;padding:20px;border-left:5px solid #0056b3;color:#003366;font-weight:bold;}</style></head><body>');
    v.document.write('<h1>SMARTCARGO ADVISORY by May Roga LLC</h1><hr><pre>' + contenido + '</pre></body></html>');
    v.document.close();
    v.print();
}

async function enviarEmail() {
    const contenido = document.getElementById('res').innerText;
    if (!contenido) return;
    const email = prompt("Email:");
    if (!email) return;
    const fd = new FormData();
    fd.append("email", email);
    fd.append("content", contenido);
    try { await fetch('/send-email', { method: 'POST', body: fd }); alert("OK"); } catch (e) { alert("Error"); }
}

// CORRECCIÓN FINAL: Borra solo la consulta y respuesta sin salir de la sesión
function limpiar() {
    imgB64 = ["", "", ""];
    chatHistory = "";
    consultInfo = { momento: "", queVe: "" };
    role = "";
    document.getElementById('prompt').value = "";
    document.getElementById('res').innerText = "";
    document.getElementById('res').style.display = "none";
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    for (let i = 1; i <= 3; i++) {
        const img = document.getElementById('v' + i);
        const txt = document.getElementById('txt-capture' + i);
        img.src = "";
        img.style.display = "none";
        txt.style.display = "block";
        const l = document.getElementById('userLang').value;
        txt.innerText = i18n[l].capture;
    }
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
    const userInput = document.getElementById('prompt').value || "Analyze";
    out.style.display = "block";
    out.innerText = i18n[l].analyzing;
    const fd = new FormData();
    fd.append("prompt", `HISTORY: ${chatHistory}. TASK: ${userInput}. Role: ${role}. Stage: ${consultInfo.momento}. Focus: ${consultInfo.queVe}`);
    fd.append("lang", l);
    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        chatHistory += ` | User: ${userInput} | Advisor: ${d.data}`;
    } catch (e) { out.innerText = "Error."; }
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("Copiado"); }

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
