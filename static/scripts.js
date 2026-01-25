// ===============================
// SMARTCARGO-AIPA by May Roga LLC
// Frontend Operational Controller
// ===============================

const form = document.getElementById("formCargo");
const semaforoStatus = document.getElementById("semaforoStatus");
const documentsList = document.getElementById("documentsList");
const advisorBox = document.getElementById("advisor");

const resetBtn = document.getElementById("resetForm");
const printBtn = document.getElementById("printPDF");
const whatsappBtn = document.getElementById("shareWhatsApp");
const translateBtn = document.getElementById("translateBtn");

const lengthInput = document.querySelector("input[name='length_cm']");
const widthInput  = document.querySelector("input[name='width_cm']");
const heightInput = document.querySelector("input[name='height_cm']");
const volumeInput = document.querySelector("input[name='volume']");

// Estado de idioma
let currentLang = "en";

// ===============================
// Cálculo automático de volumen
// ===============================
function calculateVolume() {
    const l = parseFloat(lengthInput.value);
    const w = parseFloat(widthInput.value);
    const h = parseFloat(heightInput.value);

    if (!isNaN(l) && !isNaN(w) && !isNaN(h)) {
        const volume = (l * w * h) / 1000000; // cm³ → m³
        volumeInput.value = volume.toFixed(3);
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

    // Preparar documentos
    const docs = [];
    const files = formData.getAll("documents");

    for (let i = 0; i < files.length; i++) {
        docs.push({ filename: files[i].name });
    }

    const cargoData = {
        mawb: formData.get("mawb"),
        hawb: formData.get("hawb"),
        origin: formData.get("origin"),
        destination: formData.get("destination"),
        cargo_type: formData.get("cargo_type"),
        flight_date: formData.get("flight_date"),
        weight_kg: Number(formData.get("weight_kg")),
        weight_lbs: Number(formData.get("weight_kg")) * 2.20462,
        length_cm: Number(formData.get("length_cm")),
        width_cm: Number(formData.get("width_cm")),
        height_cm: Number(formData.get("height_cm")),
        volume: Number(formData.get("volume")),
        role: formData.get("role"),
        documents: docs
    };

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams(cargoData)
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || "Validation error");
        }

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

    if (data.documents_required && data.documents_required.length > 0) {
        let html = "<strong>Required Documents:</strong><ul>";
        data.documents_required.forEach(doc => {
            html += `<li>${doc}</li>`;
        });
        html += "</ul>";
        documentsList.innerHTML = html;
    } else {
        documentsList.innerHTML = "<strong>No documents required</strong>";
    }

    advisorBox.textContent = data.advisor || "No advisory message generated.";
}

// ===============================
// Reset total
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
// WhatsApp Share
// ===============================
whatsappBtn.addEventListener("click", () => {
    const message =
`SMARTCARGO-AIPA by May Roga LLC

Operational Result:
${semaforoStatus.textContent}

Advisor:
${advisorBox.textContent}

Disclaimer:
Preventive documentary validation system.
Does not replace airline or authority decisions.`;

    const url = "https://api.whatsapp.com/send?text=" + encodeURIComponent(message);
    window.open(url, "_blank");
});

// ===============================
// Traducción EN ⇄ ES
// ===============================
translateBtn.addEventListener("click", () => {
    currentLang = currentLang === "en" ? "es" : "en";

    document.querySelectorAll("[data-en][data-es]").forEach(el => {
        el.textContent = currentLang === "en"
            ? el.getAttribute("data-en")
            : el.getAttribute("data-es");
    });
});
