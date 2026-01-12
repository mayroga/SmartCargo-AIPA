let role = "";
const i18n = {
    en: {
        promoGold: "360° STRATEGIC LOGISTICS SOLUTIONS - MAY ROGA LLC",
        promoBlue: "MITIGATING HOLDS & RETURNS. WE THINK FOR YOUR CARGO.",
        get: "EXECUTE ADVISORY",
        analyzing: "MAY ROGA LLC | MASTER VALIDATION IN PROGRESS...",
        roles: ["Trucker", "Forwarder", "Counter Staff", "Shipper/Owner"]
    },
    es: {
        promoGold: "SOLUCIONES LOGÍSTICAS ESTRATÉGICAS 360° - MAY ROGA LLC",
        promoBlue: "MITIGAMOS RETENCIONES Y RETORNOS. PENSAMOS POR TU CARGA.",
        get: "EJECUTAR ASESORÍA",
        analyzing: "MAY ROGA LLC | VALIDACIÓN MAESTRA EN CURSO...",
        roles: ["Camionero", "Forwarder", "Agente Counter", "Dueño/Shipper"]
    }
};

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('promoGold').innerHTML = `<span>${lang.promoGold}</span>`;
    document.getElementById('promoBlue').innerHTML = `<span>${lang.promoBlue}</span>`;
    document.getElementById('btn-get').innerText = lang.get;
    document.querySelectorAll('.role-btn').forEach((b, i) => b.innerText = lang.roles[i]);
}

let rec;
function startVoice() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) return;
    rec = new Speech();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    rec.start();
    rec.onresult = (e) => { document.getElementById('prompt').value = e.results[0][0].transcript; };
}
function stopVoice() { if(rec) rec.stop(); }

async function pay(amt) {
    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", document.getElementById('awb').value || "REF_MASTER");
    fd.append("user", document.getElementById('u').value);
    fd.append("p", document.getElementById('p').value);
    
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.url) window.location.href = d.url;
}

async function run() {
    if (!role) return alert("Select Role / Selecciona Rol");
    const out = document.getElementById('res');
    out.style.display = "block";
    out.innerText = i18n[document.getElementById('userLang').value].analyzing;
    
    const fd = new FormData();
    fd.append("prompt", document.getElementById('prompt').value);
    fd.append("role", role);
    fd.append("lang", document.getElementById('userLang').value);
    
    const r = await fetch('/advisory', { method: 'POST', body: fd });
    const d = await r.json();
    out.innerText = d.data;
    
    const utter = new SpeechSynthesisUtterance(d.data);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

function selRole(r, btn) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
}
