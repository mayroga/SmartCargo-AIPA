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

// Inputs de medidas
const lengthInput = document.getElementById("length_cm");
const widthInput  = document.getElementById("width_cm");
const heightInput = document.getElementById("height_cm");
const volumeInput = document.getElementById("volume");

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

    // Documentos + descripción (OBLIGATORIA)
    const docs = [];
    const files = formData.getAll("documents");
    const descriptions = formData.getAll("document_description");

    for (let i = 0; i < files.length; i++) {
        if (!descriptions[i] || descriptions[i].trim() === "") {
            alert("Each document/photo must include a description.");
            semaforoStatus.textContent = "🔴 NOT ACCEPTABLE";
            return;
        }
        docs.push({
            filename: files[i].name,
            description: descriptions[i]
        });
    }

    const cargoData = {
        mawb: formData.get("mawb"),
        hawb: formData.get("hawb"),
        origin: formData.get("origin"),
        destination: formData.get("destination"),
        cargo_type: formData.get("cargo_type"),
        flight_date: formData.get("flight_date"),

        // Medidas reales
        length_cm: Number(formData.get("length_cm")),
        width_cm: Number(formData.get("width_cm")),
        height_cm: Number(formData.get("height_cm")),
        volume_m3: Number(formData.get("volume")),

        weight: Number(formData.get("weight")),
        role: formData.get("role"),
        documents: docs
    };

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(cargoData)
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

    // Documentos
    if (data.documents && data.documents.length > 0) {
        let html = "<strong>Documents reviewed:</strong><ul>";
        data.documents.forEach(d => {
            html += `<li>${d.filename} – ${d.description}</li>`;
        });
        html += "</ul>";
        documentsList.innerHTML = html;
    } else {
        documentsList.innerHTML = "<strong>No documents provided</strong>";
    }

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
