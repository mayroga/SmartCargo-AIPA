let currentLang = 'es';

function toggleLang() {
    currentLang = currentLang === 'es' ? 'en' : 'es';
    alert(currentLang === 'es' ? 'Idioma: Español' : 'Language: English');
}

async function validateCargo() {
    const data = new FormData();
    const fields = ['mawb', 'role', 'cargo_type', 'weight', 'length', 'width', 'height'];
    
    // Validación básica de campos vacíos
    for (let f of fields) {
        let val = document.getElementById(f).value;
        if (!val) {
            alert("Por favor complete todos los campos técnicos.");
            return;
        }
        data.append(f, val);
    }
    data.append('lang', currentLang);

    // Cambio de vista
    document.getElementById('form-cargo').style.display = 'none';
    const resPage = document.getElementById('result-page');
    resPage.style.display = 'block';
    document.getElementById('analysis-text').innerText = "Procesando validación con reglas de Avianca Cargo...";

    try {
        const response = await fetch('/validate', {
            method: 'POST',
            body: data
        });

        if (!response.ok) throw new Error("Error en servidor");

        const result = await response.json();

        // Actualizar Semáforo
        const sem = document.getElementById('semaforo');
        sem.className = `semaphore ${result.status}`;
        
        const label = document.getElementById('status-label');
        label.innerText = result.status === 'GREEN' ? 'VALIDACIÓN EXITOSA' : (result.status === 'RED' ? 'CARGA RECHAZADA' : 'REVISIÓN DOCUMENTAL');
        label.style.color = result.status === 'RED' ? '#ef4444' : '#1e293b';

        // Inyectar Análisis y Legal
        document.getElementById('analysis-text').innerHTML = formatOutput(result.analysis);
        document.getElementById('legal-block').innerText = result.legal;

    } catch (error) {
        document.getElementById('analysis-text').innerText = "ERROR DE CONEXIÓN: No se pudo contactar con el backend.";
    }
}

function formatOutput(text) {
    // Convierte el formato de tabla markdown básico a HTML simple
    return text.replace(/\n/g, "<br>").replace(/\|/g, " | ");
}

function speakResult() {
    const text = document.getElementById('analysis-text').innerText;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = currentLang === 'es' ? 'es-ES' : 'en-US';
    utterance.rate = 0.9;
    speechSynthesis.speak(utterance);
}

function resetForm() {
    if (confirm("¿Desea borrar todos los datos ingresados?")) {
        document.querySelectorAll('input').forEach(i => i.value = '');
    }
}

function backToInput() {
    speechSynthesis.cancel();
    document.getElementById('result-page').style.display = 'none';
    document.getElementById('form-cargo').style.display = 'block';
}
