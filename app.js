let role = "";
let chatHistory = "";

function changeLang(l) {
    const isEn = l === 'en';
    document.getElementById('btn-get').innerText = isEn ? "EXECUTE ADVISORY" : "EJECUTAR ASESORÍA";
    // Actualizar roles si es necesario...
}

function hablar(t) {
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(t.replace(/[*#_]/g, ""));
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

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
    if (!role) return alert("Seleccione su Rol");
    const p = document.getElementById('prompt').value;
    const out = document.getElementById('res');
    out.style.display = "block"; out.innerText = "SMARTCARGO ADVISORY | ANALIZANDO...";
    
    const fd = new FormData();
    fd.append("prompt", `HISTORIAL: ${chatHistory} | CONSULTA: ${p}`);
    fd.append("lang", document.getElementById('userLang').value);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        document.getElementById('speak-btn').style.display = "block";
        chatHistory += ` Q:${p} A:${d.data} | `;
    } catch (e) {
        out.innerText = "ERROR DE CONEXIÓN CON EL CEREBRO DE MAY ROGA LLC.";
    }
}

function selRole(r, b) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function email() { 
    const body = encodeURIComponent(document.getElementById('res').innerText);
    window.location.href = `mailto:?subject=Reporte SmartCargo Advisory&body=${body}`;
}

const params = new URLSearchParams(window.location.search);
if (params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = "none";
    document.getElementById('mainApp').style.display = "block";
}
