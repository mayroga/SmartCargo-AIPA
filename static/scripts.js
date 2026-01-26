const form = document.getElementById("formCargo");
const semaforoStatus = document.getElementById("semaforoStatus");
const documentsList = document.getElementById("documentsList");
const explanationBox = document.getElementById("explanation");
const advisorBox = document.getElementById("advisor");

const resetBtn = document.getElementById("resetForm");
const printBtn = document.getElementById("printPDF");
const whatsappBtn = document.getElementById("shareWhatsApp");
const translateBtn = document.getElementById("translateBtn");

const lengthInput = document.querySelector("input[name='length_cm']");
const widthInput = document.querySelector("input[name='width_cm']");
const heightInput = document.querySelector("input[name='height_cm']");
const volumeInput = document.querySelector("input[name='volume']");

let currentLang = "en";

// ===============================
// Calcular volumen automáticamente
// ===============================
function calculateVolume() {
    const l = parseFloat(lengthInput.value);
    const w = parseFloat(widthInput.value);
    const h = parseFloat(heightInput.value);

    if (!isNaN(l) && !isNaN(w) && !isNaN(h)) {
        volumeInput.value = ((l * w * h) / 1000000).toFixed(3);
    }
}

[lengthInput, widthInput, heightInput].forEach(input => {
    input.addEventListener("input", calculateVolume);
});

// ===============================
// Submit principal
// ===============================
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    semaforoStatus.textContent = "PROCESSING…";
    explanationBox.textContent = "";
    advisorBox.textContent = "";
    documentsList.innerHTML = "";

    const formData = new FormData(form);
    const dataToSend = {};
    formData.forEach((v, k) => dataToSend[k] = v);

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Validation error");

        renderResults(data);

    } catch (err) {
        semaforoStatus.textContent = "🔴 NOT ACCEPTABLE";
        explanationBox.textContent = err.message;
    }
});

// ===============================
// Renderizar resultados con explicación legal
// ===============================
function renderResults(data) {
    semaforoStatus.textContent = data.semaforo || "🔴 NOT ACCEPTABLE";

    // Documentos
    if (data.documents_required) {
        let html = "<strong>Required Documents:</strong><ul>";
        data.documents_required.forEach(doc => {
            const missing = data.missing_docs.includes(doc) ? " (MISSING)" : "";
            html += `<li>${doc}${missing}</li>`;
        });
        html += "</ul>";
        documentsList.innerHTML = html;
    }

    // Explicación
    explanationBox.textContent = data.explanation || "No explanation generated.";

    // Asesor
    advisorBox.textContent = data.advisor || "No advisory message generated.";
}

// ===============================
// Reset total
// ===============================
resetBtn.addEventListener("click", () => {
    form.reset();
    semaforoStatus.textContent = "-";
    documentsList.innerHTML = "";
    explanationBox.textContent = "";
    advisorBox.textContent = "";
});

// ===============================
// Print / PDF
// ===============================
printBtn.addEventListener("click", () => {
    window.print();
});

// ===============================
// WhatsApp Share
// ===============================
whatsappBtn.addEventListener("click", () => {
    const message =
`SMARTCARGO-AIPA by May Roga LLC
Semáforo: ${semaforoStatus.textContent}
Documents: ${documentsList.innerText}
Explanation: ${explanationBox.textContent}
Advisor: ${advisorBox.textContent}`;

    const url = "https://api.whatsapp.com/send?text=" + encodeURIComponent(message);
    window.open(url, "_blank");
});

// ===============================
// Traducción EN ⇄ ES
// ===============================
translateBtn.addEventListener("click", () => {
    currentLang = currentLang === "en" ? "es" : "en";
    document.querySelectorAll("[data-en][data-es]").forEach(el => {
        el.textContent = currentLang === "en" ? el.getAttribute("data-en") : el.getAttribute("data-es");
    });
});
