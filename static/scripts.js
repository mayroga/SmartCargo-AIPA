const form = document.getElementById("formCargo");
const semaforoStatus = document.getElementById("semaforoStatus");
const documentsList = document.getElementById("documentsList");
const advisorBox = document.getElementById("advisor");
const resetBtn = document.getElementById("resetForm");
const printBtn = document.getElementById("printPDF");
const whatsappBtn = document.getElementById("shareWhatsApp");
const translateBtn = document.getElementById("translateBtn");

const lengthInput = document.getElementById("length_cm");
const widthInput  = document.getElementById("width_cm");
const heightInput = document.getElementById("height_cm");
const volumeInput = document.getElementById("volume");

let currentLang = "en";

// ===============================
// Volumen automático
// ===============================
function calculateVolume() {
    const l = parseFloat(lengthInput.value);
    const w = parseFloat(widthInput.value);
    const h = parseFloat(heightInput.value);
    if (!isNaN(l) && !isNaN(w) && !isNaN(h)) {
        volumeInput.value = ((l * w * h) / 1000000).toFixed(3);
    } else {
        volumeInput.value = "";
    }
}
lengthInput.addEventListener("input", calculateVolume);
widthInput.addEventListener("input", calculateVolume);
heightInput.addEventListener("input", calculateVolume);

// ===============================
// Submit principal
// ===============================
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    semaforoStatus.textContent = "PROCESSING…";
    advisorBox.textContent = "";
    documentsList.innerHTML = "";

    const formData = new FormData(form);
    const cargoData = {
        mawb: formData.get("mawb"),
        hawb: formData.get("hawb"),
        origin: formData.get("origin"),
        destination: formData.get("destination"),
        cargo_type: formData.get("cargo_type"),
        flight_date: formData.get("flight_date"),
        weight_kg: parseFloat(formData.get("weight_kg")),
        length_cm: parseFloat(formData.get("length_cm")),
        width_cm: parseFloat(formData.get("width_cm")),
        height_cm: parseFloat(formData.get("height_cm")),
        role: formData.get("role"),
        documents: formData.get("documents") // JSON string
    };

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            body: new URLSearchParams(cargoData)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Validation error");

        renderResults(data);
    } catch (err) {
        semaforoStatus.textContent = "🔴 NOT ACCEPTABLE";
        advisorBox.textContent = err.message;
    }
});

// ===============================
// Render resultados
// ===============================
function renderResults(data) {
    semaforoStatus.textContent = data.semaforo || "🔴 NOT ACCEPTABLE";

    if (data.documents_required.length > 0) {
        let html = "<strong>Documents Required:</strong><ul>";
        data.documents_required.forEach(d => html += `<li>${d}</li>`);
        html += "</ul>";
        if (data.missing_docs.length > 0) {
            html += "<strong>Missing Documents:</strong><ul>";
            data.missing_docs.forEach(d => html += `<li>${d}</li>`);
            html += "</ul>";
        }
        documentsList.innerHTML = html;
    } else {
        documentsList.innerHTML = "<strong>No documents required</strong>";
    }

    advisorBox.textContent = data.advisor || "No advisory message generated.";
}

// ===============================
// Reset
// ===============================
resetBtn.addEventListener("click", () => {
    form.reset();
    semaforoStatus.textContent = "-";
    documentsList.innerHTML = "";
    advisorBox.textContent = "";
});

// ===============================
// Print / PDF
// ===============================
printBtn.addEventListener("click", () => {
    window.print();
});

// ===============================
// WhatsApp
// ===============================
whatsappBtn.addEventListener("click", () => {
    const message =
`SMARTCARGO-AIPA by May Roga LLC

Status: ${semaforoStatus.textContent}
Advisor: ${advisorBox.textContent}`;

    const url = "https://api.whatsapp.com/send?text=" + encodeURIComponent(message);
    window.open(url, "_blank");
});

// ===============================
// Translate EN ⇄ ES
// ===============================
translateBtn.addEventListener("click", () => {
    currentLang = currentLang === "en" ? "es" : "en";
    document.querySelectorAll("[data-en][data-es]").forEach(el => {
        el.textContent = currentLang === "en" ? el.getAttribute("data-en") : el.getAttribute("data-es");
    });
});
