// ==============================================================================
// SMARTCARGO ADVISORY - LÓGICA DE INSPECCIÓN TÉCNICA (AVIANCA HUB READY)
// ==============================================================================

let selectedRole = "Expert Advisor"; // Default role para especialistas
let volData = ""; // Almacena el cálculo de rentabilidad para el reporte final

// 1. SELECCIÓN DE ROL (Para auditoría de costos)
function selRole(role, element) {
    selectedRole = role;
    document.querySelectorAll('.opt-btn').forEach(btn => btn.classList.remove('active'));
    element.classList.add('active');
}

// 2. CÁLCULO DE VOLUMEN CRÍTICO (Protección de Ganancias)
function calcVol() {
    const l = parseFloat(document.getElementById('L').value);
    const w = parseFloat(document.getElementById('W').value);
    const h = parseFloat(document.getElementById('H').value);
    const act = parseFloat(document.getElementById('actW').value);
    const unit = document.getElementById('unit').value;
    const resDiv = document.getElementById('vRes');

    if(!l || !w || !h || !act) {
        alert("Enter all dimensions to calculate chargeable weight.");
        return;
    }
    
    // IATA Standard: 6000 para CM/KG, 166 para INC/LB
    let vW = (unit === "CM") ? (l * w * h) / 6000 : (l * w * h) / 166;
    let chargeable = Math.max(act, vW);
    let loss = (vW > act) ? (vW - act).toFixed(2) : 0;

    volData = `\n[CUBIC ANALYSIS] Chargeable: ${chargeable.toFixed(2)} vs Actual: ${act} ${unit}. `;
    if(loss > 0) volData += `Alert: Loss of ${loss} ${unit} due to density.`;

    resDiv.innerHTML = `CHARGEABLE: ${chargeable.toFixed(2)} ${unit} <br> ${loss > 0 ? '⚠️ DENSITY LOSS DETECTED' : '✅ OPTIMIZED'}`;
}

// 3. PREVISUALIZACIÓN DE IMÁGENES (Alta Resolución)
function pv(event, id) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const output = document.getElementById(id);
        output.src = e.target.result;
        output.style.display = "block";
        // Ocultar el texto de ayuda dentro de la caja
        output.nextElementSibling.style.display = "none";
    };
    reader.readAsDataURL(file);
}

// 4. DICTADO DE VOZ (Para manos libres en el almacén/HUB)
function startDictation() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = (event) => {
        document.getElementById('obs').value += " " + event.results[0][0].transcript;
    };
}

// 5. EJECUCIÓN DE ASESORÍA TÉCNICA (Conexión con el Cerebro)
async function process() {
    const awb = document.getElementById('awb').value.trim();
    const evidence = document.getElementById('obs').value;
    const btn = document.getElementById('exec');
    const resBox = document.getElementById('resBox');
    const resTxt = document.getElementById('resTxt');

    if (!awb) {
        alert("Please enter AWB or Reference Number.");
        return;
    }

    // Bloqueo de UI para evitar "freezes" y duplicados
    btn.disabled = true;
    btn.innerText = "VERIFYING AVIANCA STANDARDS...";
    resBox.style.display = "block";
    resTxt.innerText = "Analyzing documentation, cubic data, and physical integrity against IATA/Avianca standards...";

    const formData = new FormData();
    // Combinamos las observaciones con los datos de volumen para que la IA los analice
    formData.append("prompt", evidence + volData);
    formData.append("role", selectedRole);
    formData.append("awb", awb);

    try {
        // Cambia esta URL por tu URL real de Render
        const response = await fetch('https://tu-backend.onrender.com/advisory', { 
            method: 'POST', 
            body: formData 
        });
        const result = await response.json();
        resTxt.innerText = result.data;
    } catch (error) {
        resTxt.innerText = "CONNECTION ERROR: Terminal network lost. Please verify your connection to the Technical Hub.";
    } finally {
        btn.disabled = false;
        btn.innerText = "Execute Technical Advisory";
        // Scroll suave hacia la respuesta
        resBox.scrollIntoView({ behavior: 'smooth' });
    }
}

// 6. FUNCIONES DE SALIDA (Voz y WhatsApp)
function speak() {
    window.speechSynthesis.cancel();
    const text = document.getElementById('resTxt').innerText;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-US';
    window.speechSynthesis.speak(utter);
}

function shareWS() {
    const text = document.getElementById('resTxt').innerText;
    const awb = document.getElementById('awb').value;
    const url = `https://wa.me/?text=${encodeURIComponent("*SMARTCARGO ADVISORY REPORT - AWB: " + awb + "*\n\n" + text)}`;
    window.open(url, '_blank');
}
