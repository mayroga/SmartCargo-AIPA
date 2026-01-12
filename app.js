let role = "";
let chatHistory = []; // Array para manejar memoria selectiva

const i18n = {
    en: { get: "EXECUTE ADVISORY", roles: ["Trucker", "Forwarder", "Counter Staff", "Shipper/Owner"], analyzing: "SMARTCARGO | ANALYZING..." },
    es: { get: "EJECUTAR ASESORÍA", roles: ["Camionero", "Forwarder", "Agente Counter", "Dueño/Shipper"], analyzing: "SMARTCARGO | ANALIZANDO..." }
};

function changeLang(l) {
    const lang = i18n[l];
    document.getElementById('btn-get').innerText = lang.get;
    const btns = document.querySelectorAll('.role-btn');
    lang.roles.forEach((text, i) => { if(btns[i]) btns[i].innerText = text; });
}

function scRead(e, n) {
    const r = new FileReader();
    r.onload = () => {
        const img = document.getElementById('v' + n);
        img.src = r.result; img.style.display = "block";
        document.getElementById('cap' + n).style.display = "none";
    };
    if(e.target.files[0]) r.readAsDataURL(e.target.files[0]);
}

function hablar(t) {
    window.speechSynthesis.cancel();
    const cleanText = t.replace(/🔊/g, "").replace(/[*#_]/g, "").replace(/-/g, " ");
    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

// IA EXECUTION
async function run() {
    const pInput = document.getElementById('prompt');
    const out = document.getElementById('res');
    const btn = document.getElementById('btn-get');
    const lang = document.getElementById('userLang').value;

    if (!role) return alert("Select Role / Selecciona Rol");
    if (!pInput.value.trim()) return alert("Write something / Escribe algo");

    // UI Estado: Bloquear para evitar clics dobles (causa de freezes)
    btn.disabled = true;
    out.style.display = "block";
    out.innerText = i18n[lang].analyzing;
    document.getElementById('speak-btn').style.display = "none";

    // Enviamos solo los últimos 4 mensajes del historial para ligereza
    const historySnippet = chatHistory.slice(-4).join(" | ");

    const fd = new FormData();
    fd.append("prompt", pInput.value);
    fd.append("history", historySnippet);
    fd.append("role", role);
    fd.append("lang", lang);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        if (!r.ok) throw new Error("Server Error");
        const d = await r.json();
        
        out.innerText = d.data;
        document.getElementById('speak-btn').style.display = "block";
        
        // Guardar en historial
        chatHistory.push(`Q:${pInput.value}`, `A:${d.data}`);
        pInput.value = ""; // Limpiar entrada
    } catch (e) {
        out.innerText = "ERROR DE CONEXIÓN: El cerebro de la IA no responde. Reintenta.";
    } finally {
        btn.disabled = false;
    }
}

function selRole(r, b) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
}

function ws() {
    const text = document.getElementById('res').innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}

function email() {
    const text = document.getElementById('res').innerText;
    window.location.href = `mailto:?subject=SMARTCARGO REPORT&body=${encodeURIComponent(text)}`;
}

// Login Detect
const params = new URLSearchParams(window.location.search);
if (params.get('access') === 'granted') {
    document.getElementById('accessSection').style.display = "none";
    document.getElementById('mainApp').style.display = "block";
}
