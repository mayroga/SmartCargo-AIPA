let role = "";
let chatHistory = "";

// --- SISTEMA DE CAPTURA DE EVIDENCIA (DOS CÁMARAS) ---
function scRead(e, n) {
    const r = new FileReader();
    r.onload = () => {
        const img = document.getElementById('v' + n);
        img.src = r.result; 
        img.style.display = "block";
        // Ocultamos el icono de texto al cargar la imagen
        document.getElementById('cap' + n).style.display = "none";
    };
    r.readAsDataURL(e.target.files[0]);
}

// --- SALIDA DE VOZ (BOCINA) CON LIMPIEZA QUIRÚRGICA ---
function hablar(t) {
    window.speechSynthesis.cancel();
    // Filtro para eliminar asteriscos, almohadillas y guiones para lectura profesional
    const cleanText = t.replace(/🔊/g, "").replace(/[*#_]/g, "").replace(/-/g, " ");
    const utter = new SpeechSynthesisUtterance(cleanText);
    
    // Detectamos el idioma del sistema
    utter.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    window.speechSynthesis.speak(utter);
}

// --- ENTRADA DE VOZ (MICRÓFONO - SPEECH TO TEXT) ---
let rec;
function startVoice() {
    const S = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!S) return alert("Navegador no soporta dictado por voz.");
    
    rec = new S();
    rec.lang = document.getElementById('userLang').value === 'es' ? 'es-US' : 'en-US';
    rec.onresult = (e) => {
        document.getElementById('prompt').value = e.results[0][0].transcript;
    };
    rec.start();
}

function stopVoice() {
    if(rec) rec.stop();
}

// --- GESTIÓN DE PAGOS Y ACCESO MAESTRO ---
async function pay(amt) {
    const awb = document.getElementById('awb').value || "REF_LOGISTICA";
    const user = document.getElementById('u').value;
    const pass = document.getElementById('p').value;

    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", awb);
    fd.append("user", user);
    fd.append("p", pass);
    
    try {
        const r = await fetch('/create-payment', { method: 'POST', body: fd });
        const d = await r.json();
        if (d.url) {
            window.location.href = d.url;
        } else {
            alert("Error en validación o pago.");
        }
    } catch (e) {
        alert("Fallo de conexión con el servidor de cobros.");
    }
}

// --- EJECUCIÓN DE ASESORÍA ESTRATÉGICA ---
async function run() {
    const promptInput = document.getElementById('prompt').value;
    const out = document.getElementById('res');
    
    if (!role) return alert("Por favor, seleccione su Rol antes de ejecutar.");
    if (!promptInput) return alert("Describa la situación técnica.");

    out.style.display = "block";
    out.innerText = "SMARTCARGO ADVISORY by MAY ROGA LLC | Analizando...";
    document.getElementById('speak-btn').style.display = "none";

    const fd = new FormData();
    // Enviamos el historial acumulado para que la IA mantenga el hilo
    fd.append("prompt", `HISTORIAL PREVIO: ${chatHistory} | CONSULTA ACTUAL: ${promptInput}`);
    fd.append("role", role);
    fd.append("lang", document.getElementById('userLang').value);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        
        out.innerText = d.data;
        // Mostramos el botón de la bocina solo cuando hay respuesta
        document.getElementById('speak-btn').style.display = "block";
        
        // Actualizamos el historial para la siguiente pregunta
        chatHistory += ` Usuario: ${promptInput} AI: ${d.data} | `;
        
    } catch (e) {
        out.innerText = "ERROR CRÍTICO: El Cerebro de MAY ROGA LLC no responde. Reintente.";
    }
}

// --- SELECTOR DE ROL ---
function selRole(r, b) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(x => x.classList.remove('selected'));
    b.classList.add('selected');
}

// --- EXPORTACIÓN DE REPORTES ---
function ws() {
    const text = document.getElementById('res').innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent("REPORTE SMARTCARGO: " + text)}`, '_blank');
}

function email() {
    const text = document.getElementById('res').innerText;
    const subject = "Asesoría Estratégica MAY ROGA LLC";
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(text)}`;
}

// --- DETECCIÓN DE ACCESO POST-PAGO ---
window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('access') === 'granted') {
        document.getElementById('accessSection').style.display = "none";
        document.getElementById('mainApp').style.display = "block";
    }
});
