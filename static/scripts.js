/* SMARTCARGO-AIPA BY MAY ROGA LLC - Motor de Ejecución Técnica */

let currentLang = 'es';
let synth = window.speechSynthesis;

/**
 * Alterna el idioma global del sistema
 */
function toggleLang() {
    currentLang = currentLang === 'es' ? 'en' : 'es';
    const msg = currentLang === 'es' ? "Idioma: ESPAÑOL" : "Language: ENGLISH";
    alert(msg);
}

/**
 * Valida la carga contra regulaciones Avianca/IATA/DOT/TSA/CBP
 */
async function validateCargo() {
    const fields = ['mawb', 'role', 'cargo_type', 'weight', 'length', 'width', 'height'];
    const data = new FormData();
    
    // Validación de integridad de datos
    for (const id of fields) {
        const element = document.getElementById(id);
        if (!element || !element.value) {
            alert(currentLang === 'es' ? "ERROR: Datos técnicos incompletos." : "ERROR: Incomplete technical data.");
            return;
        }
        data.append(id, element.value);
    }
    data.append('lang', currentLang);

    // Transición de interfaz
    document.getElementById('form-cargo').style.display = 'none';
    const resPage = document.getElementById('result-page');
    resPage.style.display = 'block';
    document.getElementById('analysis-text').innerText = currentLang === 'es' ? "EJECUTANDO PROTOCOLO DE VALIDACIÓN..." : "EXECUTING VALIDATION PROTOCOL...";

    try {
        const response = await fetch('/validate', {
            method: 'POST',
            body: data
        });

        if (!response.ok) throw new Error("Server Connection Failed");

        const result = await response.json();

        // Actualización de Semáforo Visual
        const sem = document.getElementById('semaforo');
        sem.className = `semaphore ${result.status}`;
        
        // Etiqueta de Estado
        const label = document.getElementById('status-label');
        label.innerText = result.status === 'GREEN' ? "ACEPTABLE / COMPLIANT" : (result.status === 'RED' ? "RECHAZADO / REJECTED" : "REVISIÓN / WARNING");
        label.style.color = result.status === 'RED' ? '#b91c1c' : '#0f172a';

        // Renderizado de Análisis Técnico (Azul) y Legal (Rojo)
        document.getElementById('analysis-text').innerHTML = parseMarkdownTable(result.analysis);
        document.getElementById('legal-block').innerText = result.legal;

    } catch (error) {
        document.getElementById('analysis-text').innerText = "ERROR DE SISTEMA: Fallo en la conexión con el nodo de cumplimiento.";
        console.error(error);
    }
}

/**
 * Ejecuta la lectura auditiva del asesor (Bocina)
 */
function speakResult() {
    if (synth.speaking) synth.cancel();
    
    const text = document.getElementById('analysis-text').innerText;
    const utterance = new SpeechSynthesisUtterance(text);
    
    utterance.lang = currentLang === 'es' ? 'es-ES' : 'en-US';
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    
    synth.speak(utterance);
}

/**
 * Borrado total de formulario y reinicio de estado
 */
function resetForm() {
    if (confirm(currentLang === 'es' ? "¿Confirmar borrado de datos?" : "Confirm data deletion?")) {
        document.querySelectorAll('input, select').forEach(el => el.value = '');
        synth.cancel();
    }
}

/**
 * Retorno al ingreso de datos
 */
function backToInput() {
    synth.cancel();
    document.getElementById('result-page').style.display = 'none';
    document.getElementById('form-cargo').style.display = 'block';
}

/**
 * Formatea tablas de texto a estructura visual clara
 */
function parseMarkdownTable(text) {
    // Reemplaza saltos de línea y asegura que las tablas de la IA se vean profesionales
    return text
        .replace(/\n/g, '<br>')
        .replace(/\|/g, '<span style="color:#cbd5e1">|</span>');
}
