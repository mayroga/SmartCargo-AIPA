let imgB64 = ["", "", ""];
let role = "";
let consultInfo = { momento: "", queVe: "" };
let chatHistory = "";

const i18n = {
    en: {
        legal: "SMARTCARGO ADVISORY by May Roga LLC | INDEPENDENT PRIVATE ADVISORY. NOT IATA, DOT, TSA, OR CBP. ALL RESPONSES ARE STRATEGIC SUGGESTIONS ONLY.",
        promoGold: "360° STRATEGIC LOGISTICS SOLUTIONS - SMARTCARGO ADVISORY BY MAY ROGA LLC",
        promoBlue: "MITIGATING HOLDS, RETURNS, SAVING MONEY. WE THINK AND WORK ON YOUR CARGO.",
        capture: " UPLOAD DOC",
        get: "EXECUTE ADVISORY",
        prompt: "Paste dimensions, weights or describe what you see...",
        analyzing: "SMARTCARGO BRAIN CALCULATING...",
        askMomento: "When is this happening? \n1. Starting \n2. Problem Now \n3. It happened",
        askQueVe: "What are you looking at? \n1. Docs \n2. Cargo \n3. Authority \n4. Not sure",
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
        prompt: "Pega medidas, pesos o describe lo que tienes ahí...",
        analyzing: "CEREBRO SMARTCARGO CALCULANDO...",
        askMomento: "¿Cuándo está pasando esto? \n1. Empezando \n2. Problema ahora \n3. Ya pasó",
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
    fd.append("prompt", `HISTORY: ${chatHistory}. TASK: ${userInput}. Role: ${role}. Stage: ${consultInfo.momento}. Focus: ${consultInfo.queVe}`);
    fd.append("lang", l);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        chatHistory += ` | User: ${userInput} | Advisor: ${d.data}`;
    } catch (e) { out.innerText = "Error connecting to Brain."; }
}

function imprimirResultado() {
    const contenido = document.getElementById('res').innerText;
    const ventana = window.open('', '', 'height=600,width=800');
    ventana.document.write('<html><head><title>SmartCargo Advisory Report</title>');
    ventana.document.write('<style>body{font-family:Arial; padding:40px; line-height:1.6;} pre{white-space:pre-wrap; background:#f4f4f4; padding:20px; border-left:5px solid #d4af37;}</style></head><body>');
    ventana.document.write('<h1>MAY ROGA LLC - SMARTCARGO Report</h1>');
    ventana.document.write('<pre>' + contenido + '</pre>');
    ventana.document.write('</body></html>');
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

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("OK"); }
function limpiar() { location.reload(); }

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
