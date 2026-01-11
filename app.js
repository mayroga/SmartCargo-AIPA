let role = "";
let chatHistory = "";

function selRole(r, el) {
    role = r;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
}

async function run() {
    const l = document.getElementById('userLang').value;
    if (!role) return alert("Por favor seleccione su Rol.");
    
    const out = document.getElementById('res');
    const input = document.getElementById('prompt').value;
    if (!input) return alert("Ingrese información de la carga.");

    out.style.display = "block";
    out.innerText = "CEREBRO SMARTCARGO CALCULANDO Y PROYECTANDO...";

    const fd = new FormData();
    fd.append("prompt", `Historial: ${chatHistory}. Entrada actual: ${input}. Rol: ${role}`);
    fd.append("lang", l);

    try {
        const r = await fetch('/advisory', { method: 'POST', body: fd });
        const d = await r.json();
        out.innerText = d.data;
        chatHistory += ` | Cliente: ${input} | Advisor: ${d.data}`;
    } catch (e) {
        out.innerText = "Error de conexión con el Cerebro Operativo.";
    }
}

function imprimirResultado() {
    const contenido = document.getElementById('res').innerText;
    const ventana = window.open('', '', 'height=600,width=800');
    ventana.document.write('<html><head><title>SmartCargo Advisory Report</title>');
    ventana.document.write('<style>body{font-family:Arial; padding:30px;} pre{white-space:pre-wrap; border:1px solid #ccc; padding:20px;}</style></head><body>');
    ventana.document.write('<h1>Reporte de Asesoría - May Roga LLC</h1>');
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
    alert("Enviado con éxito.");
}

function ws() { window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById('res').innerText)); }
function copy() { navigator.clipboard.writeText(document.getElementById('res').innerText); alert("Copiado."); }
function limpiar() { location.reload(); }
