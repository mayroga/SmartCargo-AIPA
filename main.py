// ===============================
// SMARTCARGO-AIPA Frontend Controller
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
const lengthInput = form.elements["length_cm"];
const widthInput = form.elements["width_cm"];
const heightInput = form.elements["height_cm"];
const volumeInput = form.elements["volume"];

// Idioma
let currentLang = "es";

// ===============================
// Cálculo automático de volumen
// ===============================
function calculateVolume() {
    const l = parseFloat(lengthInput.value);
    const w = parseFloat(widthInput.value);
    const h = parseFloat(heightInput.value);
    if (!isNaN(l) && !isNaN(w) && !isNaN(h)) {
        const volume = (l * w * h) / 1000000;
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
    const docs = Array.from(formData.getAll("documents")).map(f => ({ filename: f.name }));

    const cargoData = {
        mawb: formData.get("mawb"),
        hawb: formData.get("hawb"),
        origin: formData.get("origin"),
        destination: formData.get("destination"),
        cargo_type: formData.get("cargo_type"),
        flight_date: formData.get("flight_date"),
        weight_kg: Number(formData.get("weight_kg")),
        length_cm: Number(formData.get("length_cm")),
        width_cm: Number(formData.get("width_cm")),
        height_cm: Number(formData.get("height_cm")),
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
    semaforoStatus.textContent = data.semaforo;
    documentsList.innerHTML = "<strong>Documents Reviewed:</strong><ul>" + 
        (data.documents_required || []).map(d => `<li>${d}</li>`).join("") + "</ul>";
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
printBtn.addEventListener("click", () => window.print());

// ===============================
// WhatsApp Share
// ===============================
whatsappBtn.addEventListener("click", () => {
    const message =
`SMARTCARGO-AIPA by May Roga LLC

Semáforo: ${semaforoStatus.textContent}
Advisor:
${advisorBox.textContent}`;
    window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent(message), "_blank");
});

// ===============================
// Traducción ES ⇄ EN
// ===============================
translateBtn.addEventListener("click", () => {
    currentLang = currentLang === "es" ? "en" : "es";
    document.querySelectorAll("[data-en][data-es]").forEach(el => {
        el.textContent = currentLang === "en" ? el.getAttribute("data-en") : el.getAttribute("data-es");
    });
});
