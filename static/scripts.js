let currentLang = "en";

function toggleLang() {
    currentLang = currentLang === "en" ? "es" : "en";
    alert(currentLang === "es" ? "Idioma cambiado a Español" : "Language changed to English");
}

async function validate() {
    const data = new FormData();
    data.append("mawb", document.getElementById("mawb").value);
    data.append("role", document.getElementById("role").value);
    data.append("cargo_type", document.getElementById("cargo_type").value);
    data.append("weight", document.getElementById("weight").value);
    data.append("height", document.getElementById("height").value);
    data.append("length", document.getElementById("length").value);
    data.append("width", document.getElementById("width").value);
    data.append("lang", currentLang);

    document.getElementById("form-container").classList.add("hidden");
    const resDiv = document.getElementById("result-page");
    resDiv.classList.remove("hidden");
    document.getElementById("ai-analysis").innerText = "Validando con SMARTCARGO-AIPA...";

    try {
        const response = await fetch("/validate", { method: "POST", body: data });
        const result = await response.json();

        // Aplicar Semáforo
        const circle = document.getElementById("semaphore-circle");
        circle.className = `semaphore ${result.status}`;
        
        document.getElementById("status-title").innerText = result.status === "GREEN" ? "ACEPTABLE" : (result.status === "RED" ? "NO ACEPTABLE" : "REVISIÓN");
        
        // El análisis viene con tablas de la IA
        document.getElementById("ai-analysis").innerHTML = formatMarkdownTable(result.analysis);
        document.getElementById("legal-disclaimer").innerText = result.legal;

    } catch (e) {
        document.getElementById("ai-analysis").innerText = "Error de conexión.";
    }
}

function readResult() {
    const text = document.getElementById("ai-analysis").innerText;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = currentLang === "es" ? "es-ES" : "en-US";
    speechSynthesis.speak(utterance);
}

function clearAll() {
    document.querySelectorAll("input").forEach(i => i.value = "");
    alert("Datos borrados.");
}

function backToForm() {
    document.getElementById("result-page").classList.add("hidden");
    document.getElementById("form-container").classList.remove("hidden");
    speechSynthesis.cancel();
}

// Formateador simple de tablas Markdown para visualización limpia
function formatMarkdownTable(text) {
    return text.replace(/\n/g, "<br>").replace(/\|/g, "│");
}
