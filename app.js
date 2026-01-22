// VARIABLES DE ESTADO
let selectedRole = "";
let chatHistory = [];
const synth = window.speechSynthesis;

// 1. GESTIÓN DE IDIOMAS (Utiliza el objeto 'i18n' que estará en config.js)
function toggleLang(lang) {
    const d = i18n[lang];
    document.getElementById('legalText').innerHTML = d.legal;
    document.getElementById('mainTitle').innerText = d.title;
    document.getElementById('promoText').innerText = d.promo;
    document.getElementById('execBtn').innerText = d.exec;
    document.getElementById('prompt').placeholder = d.placeholder;
    
    // Actualizar nombres de roles
    const roles = ["r1", "r2", "r3", "r4"];
    roles.forEach((id, i) => {
        document.getElementById(id).innerText = d.roles[i];
    });
}

// 2. PREVISUALIZACIÓN DE IMÁGENES
function preview(e, n) {
    const reader = new FileReader();
    reader.onload = () => {
        const img = document.getElementById('view' + n);
        img.src = reader.result;
        img.style.display = "block";
        document.getElementById('lab' + n).style.display = "none";
    };
    if(e.target.files[0]) reader.readAsDataURL(e.target.files[0]);
}

// 3. SELECCIÓN DE ROL
function setRole(role, btn) {
    selectedRole = role;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
}

// 4. EJECUCIÓN DE ASESORÍA (IA)
async function runAdvisory() {
    const pInput = document.getElementById('prompt');
    const out = document.getElementById('responseText');
    const resBox = document.getElementById('res');
    const btn = document.getElementById('execBtn');
    const lang = document.getElementById('userLang').value;

    if (!selectedRole) return alert(lang === 'es' ? "Selecciona un Rol" : "Select a Role");
    if (!pInput.value.trim()) return alert(lang === 'es' ? "Escribe tu consulta" : "Write your query");

    // Bloqueo de UI para evitar "Freezes"
    btn.disabled = true;
    btn.innerText = lang === 'es' ? "ANALIZANDO..." : "ANALYZING...";
    resBox.style.display = "block";
    out.innerText = "...";

    // Preparar historial (últimos 4 para ligereza)
    const historySnippet = chatHistory.slice(-4).join(" | ");

    const fd = new FormData();
    fd.append("prompt", pInput.value);
    fd.append("history", historySnippet);
    fd.append("role", selectedRole);
    fd.append("lang", lang);

    try {
        const response = await fetch('/advisory', { method: 'POST', body: fd });
        const result = await response.json();
        
        out.innerText = result.data;
        chatHistory.push(`Q:${pInput.value}`, `A:${result.data}`);
        pInput.value = ""; // Limpiar entrada
    } catch (err) {
        out.innerText = "Error: Connection lost. Reintenta.";
    } finally {
        btn.disabled = false;
        btn.innerText = i18n[lang].exec;
    }
}

// 5. VOZ Y COMPARTIR
function readAloud() {
    synth.cancel();
    const text = document.getElementById('responseText').innerText;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    synth.speak(utter);
}

// Dictado por voz (Micrófono)
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.onresult = (e) => {
    document.getElementById('prompt').value = e.results[0][0].transcript;
};

document.getElementById('micBtn').onclick = () => {
    recognition.start();
};

// Funciones de Envío
function shareWS() {
    const t = document.getElementById('responseText').innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(t)}`, '_blank');
}

function shareEmail() {
    const t = document.getElementById('responseText').innerText;
    window.location.href = `mailto:?subject=SMARTCARGO ADVISORY&body=${encodeURIComponent(t)}`;
}

// Lógica de Acceso (Simulada para el ejemplo)
function processPay(amt) {
    alert(`Redirigiendo a Checkout de $${amt}...`);
    // Aquí iría la lógica de Stripe. Para pruebas:
    document.getElementById('accessSection').style.display = "none";
    document.getElementById('mainApp').style.display = "block";
}

function showLogin() {
    const f = document.getElementById('loginForm');
    f.style.display = f.style.display === 'none' ? 'block' : 'none';
}
