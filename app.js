// ==============================================================================
// SMARTCARGO ADVISORY - LÓGICA OPERATIVA (FOTO-ESTRUCTURA)
// ==============================================================================

let selectedRole = "";
let isCritical = false;

// 1. SELECCIÓN DE ROL Y PRECIO
function selRole(role, element, critical = false) {
    selectedRole = role;
    isCritical = critical;
    // Remover clase 'selected' de todos los botones de rol
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    // Resaltar el botón seleccionado
    element.classList.add('selected');
}

// 2. DESBLOQUEO DE APLICACIÓN (VALIDATE & ACCESS)
function unlockApp() {
    const awb = document.getElementById('awb').value.trim();
    if (!selectedRole) {
        alert("Please select a Role first / Por favor seleccione un Rol.");
        return;
    }
    if (!awb) {
        alert("Please enter a Reference or AWB / Ingrese Referencia o AWB.");
        return;
    }
    // Mostrar sección principal
    document.getElementById('mainApp').style.display = "block";
    document.getElementById('awb').disabled = true;
}

// 3. PREVISUALIZACIÓN DE IMÁGENES (LAS 3 CAJAS)
function pv(event, index) {
    const reader = new FileReader();
    reader.onload = function() {
        const output = document.getElementById('v' + index);
        output.src = reader.result;
        output.style.display = "block";
        // Ocultar el número/texto de fondo
        output.parentElement.style.color = "transparent";
    };
    if(event.target.files[0]) {
        reader.readAsDataURL(event.target.files[0]);
    }
}

// 4. DICTADO DE VOZ (MICROPHONE)
function startDictation() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US'; // Puede cambiarse dinámicamente
    recognition.start();

    recognition.onresult = (event) => {
        document.getElementById('evidence').value = event.results[0][0].transcript;
    };
}

// 5. EJECUCIÓN DE SOLUCIÓN TÉCNICA
async function getSolution() {
    const evidence = document.getElementById('evidence').value;
    const btn = document.getElementById('btn-solution');
    const responseArea = document.getElementById('responseArea');
    const resText = document.getElementById('resText');

    if (!evidence.trim()) {
        alert("Please describe the findings / Por favor describa los hallazgos.");
        return;
    }

    // Estado de carga para evitar "Freezes"
    btn.disabled = true;
    btn.innerText = "ANALYZING TECHNICAL DATA...";
    responseArea.style.display = "block";
    resText.innerText = "Generating specialized advisory...";

    const formData = new FormData();
    formData.append("prompt", evidence);
    formData.append("role", selectedRole);
    formData.append("awb", document.getElementById('awb').value);

    try {
        const response = await fetch('/advisory', { 
            method: 'POST', 
            body: formData 
        });
        const result = await response.json();
        resText.innerText = result.data;
    } catch (error) {
        resText.innerText = "CONNECTION ERROR: The technical brain is not responding. Please retry.";
    } finally {
        btn.disabled = false;
        btn.innerText = "Get Technical Solution";
    }
}

// 6. FUNCIONES DE SALIDA (VOZ Y COMPARTIR)
function speak() {
    window.speechSynthesis.cancel();
    const text = document.getElementById('resText').innerText;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-US';
    window.speechSynthesis.speak(utter);
}

function sendWS() {
    const text = document.getElementById('resText').innerText;
    const url = `https://wa.me/?text=${encodeURIComponent("SMARTCARGO ADVISORY: " + text)}`;
    window.open(url, '_blank');
}
