let imgB64 = ["", "", ""];
let role = "";
let consultInfo = { momento: "", queVe: "" };
let chatHistory = "";

const i18n = {
    en: {
        legal: "INDEPENDENT PRIVATE ADVISORY. WE ARE NOT IATA, DOT, TSA, OR CBP. OUR RESPONSES ARE STRATEGIC SUGGESTIONS.",
        promoGold: "360° STRATEGIC SOLUTIONS BY MAY ROGA LLC - PRIVATE LOGISTICS ADVISORY LEADERS - SMARTCARGO ADVISORY",
        promoBlue: "WE MITIGATE HOLDS, RETURNS, SAVE MONEY, WE THINK AND WORK ON YOUR CARGO",
        capture: "📷 GIVE ME THE DOC",
        get: "RECEIVE ADVISORY",
        prompt: "Tell me what you see, I'm listening to suggest the best path...",
        analyzing: "MAY ROGA LLC | ANALYZING STRATEGY...",
        askMomento: "When is this happening? \n1. Starting \n2. I have a problem now \n3. It already happened",
        askQueVe: "What do you have in your hand? \n1. Papers \n2. Things/Cargo \n3. A person/Officer \n4. I don't know",
        roleAlert: "Please select your role",
        clear: "NEW CONSULT",
        u: "Username", p: "Password", roles: ["Driver", "Agent", "Warehouse", "Owner"]
    },
    es: {
        legal: "ASESORÍA PRIVADA INDEPENDIENTE. NO SOMOS IATA, DOT, TSA O CBP. NUESTRAS RESPUESTAS SON SUGERENCIAS ESTRATÉGICAS.",
        promoGold: "SOLUCIONES ESTRATÉGICAS 360° BY MAY ROGA LLC - LÍDERES EN ASESORÍA LOGÍSTICA PRIVADA - SMARTCARGO ADVISORY",
        promoBlue: "MITIGAMOS RETENCIONES, RETORNOS, AHORRAMOS DINERO, PENSAMOS Y TRABAJAMOS EN TU MERCANCIA",
        capture: "📷 MÁNDAME EL DOC",
        get: "RECIBIR ASESORÍA",
        prompt: "Dime qué tienes ahí, te escucho para asesorarte...",
        analyzing: "MAY ROGA LLC | ANALIZANDO ESTRATEGIA...",
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
        document.getElementById('txt-capture' + i).innerText = lang.capture;
    }
    for (let i = 1; i <= 4; i++) {
        document.getElementById('role' + i).innerText = lang.roles[i-1];
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
    imgB64 = ["", "", ""]; chatHistory = "";
    for (let i = 1; i <= 3; i++) {
        const img = document.getElementById('v' + i);
        const txt = document.getElementById('txt-capture' + i);
        if (img) { img.src = ""; img.style.display = "none"; }
        if (txt) txt.style.display = "block";
    }
    document.getElementById('prompt').value = "";
    document.getElementById('res').innerText = "";
    document.getElementById('res').style.display = "none";
    consultInfo = { momento: "", queVe: "" }; role = "";
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
    const userInput = document.getElementById('prompt').value || "Check updates";
    out.style.display = "block"; out.innerText = i18n[l].analyzing;

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
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("OK"); }

async function pay(amt) {
    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", document.getElementById('awb').value || "REF");
    fd.append("user", document.getElementById('u').value);
    fd.append("password", document.getElementById('p').value);
    
    // Llamada directa al servidor para verificar pago o acceso maestro
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.url) window.location.href = d.url;
    else if (d.error) alert(d.error);
}
