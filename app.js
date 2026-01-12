let role = "";
let chatHistory = "";
const i18n = {
    en: { promoGold: "360° STRATEGIC LOGISTICS - MAY ROGA LLC", get: "EXECUTE ADVISORY", roles: ["Trucker", "Forwarder", "Counter", "Shipper"] },
    es: { promoGold: "SOLUCIONES LOGÍSTICAS 360° - MAY ROGA LLC", get: "EJECUTAR ASESORÍA", roles: ["Camionero", "Forwarder", "Counter", "Dueño/Shipper"] }
};

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('promoGold').innerHTML = `<span>${lang.promoGold}</span>`;
    document.getElementById('btn-get').innerText = lang.get;
    document.querySelectorAll('.role-btn').forEach((b, i) => b.innerText = lang.roles[i]);
}

function scRead(e, n) {
    const r = new FileReader();
    r.onload = () => {
        const img = document.getElementById('v' + n);
        img.src = r.result; img.style.display = "block";
        document.getElementById('txt-capture' + n).style.display = "none";
    };
    r.readAsDataURL(e.target.files[0]);
}

function hablar(t) {
    window.speechSynthesis.cancel();
    const limpia = t.replace(/[*#_]/g, "").replace(/-/g, " ");
    const utter = new SpeechSynthesisUtterance(limpia);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

let rec;
function startVoice() {
    const S = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!S) return;
    rec = new S();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    rec.onresult = (e) => document.getElementById('prompt').value = e.results[0][0].transcript;
    rec.start();
}
function stopVoice() { if(rec) rec.stop(); }

async function pay(amt) {
    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", document.getElementById('awb').value || "REF");
    fd.append("user", document.getElementById('u').value);
    fd.append("p", document.getElementById('p').value);
    const r = await fetch('/create-payment', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.url) window.location.href = d.url;
}

async function run() {
    if (!role) return alert("Selecciona Rol");
    const p = document.getElementById('prompt').value;
    const out = document.getElementById('res');
    out.style.display = "block"; out.innerText = "Validando...";
    const fd = new FormData();
    fd.append("prompt", `HISTORIAL: ${chatHistory} | CONSULTA: ${p}`);
    fd.append("role", role);
    fd.append("lang", document.getElementById('userLang').value);
    const r = await fetch('/advisory', { method: 'POST', body: fd });
    const d = await r.json();
    out.innerText = d.data;
    chatHistory += ` Q:${p} A:${d.data} |`;
    hablar(d.data);
}

function selRole(r, b) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function email() { window.open("mailto:?subject=Asesoría SmartCargo&body=" + encodeURIComponent(document.getElementById('res').innerText)); }
