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

// VOZ HUMANA: LECTURA LIMPIA SIN CARACTERES TÉCNICOS
function escuchar() {
    let text = document.getElementById('res').innerText;
    if (!text || text.includes("...")) return;

    // Limpieza de símbolos para que suene como humano
    text = text.replace(/[*#\\_]/g, ""); 
    text = text.replace(/\[.*?\]/g, ""); 
    text = text.replace(/-/g, " "); 

    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    const currentLang = document.getElementById('userLang').value;
    utter.lang = currentLang === 'es' ? 'es-US' : 'en-US';
    utter.rate = 0.95; 
    window.speechSynthesis.speak(utter);
}

// SALIDAS PROFESIONALES
function imprimirPDF() {
    const contenido = document.getElementById('res').innerText;
    if (!contenido) return;
    const v = window.open('', '', 'height=700,width=900');
    v.document.write('<html><head><title>SmartCargo Report</title><style>body{font-family:sans-serif;padding:40px;line-height:1.6;}pre{white-space:pre-wrap;background:#f9f9f9;padding:20px;border-left:5px solid #d4af37; font-size:14px;}</style></head><body>');
    v.document.write('<h1>SMARTCARGO ADVISORY by May Roga LLC</h1><p>Technical Prevention & Education</p><hr>');
    v.document.write('<pre>' + contenido + '</pre></body></html>');
    v.document.close();
    v.print();
}

async function enviarEmail() {
    const contenido = document.getElementById('res').innerText;
    if (!contenido) return;
    const email = prompt("Email del Cliente / Client Email:");
    if (!email) return;
    const fd = new FormData();
    fd.append("email", email);
    fd.append("content", contenido);
    try {
        await fetch('/send-email', { method: 'POST', body: fd });
        alert("Enviado / Sent");
    } catch (e) { alert("Error"); }
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
    const userInput = document.getElementById('prompt').value || "Analyze update";
    out.style.display = "block";
    out.innerText = i18n[l].analyzing;

    const fd = new FormData();
    fd.append("prompt", `HISTORY: ${chatHistory}. CURRENT_TASK: ${userInput}. Role: ${role}. Stage: ${consultInfo.momento}. Focus: ${consultInfo.queVe}`);
    fd.append("lang", l);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        chatHistory += ` | User: ${userInput} | Advisor: ${d.data}`;
    } catch (e) { out.innerText = "Error de conexión."; }
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
