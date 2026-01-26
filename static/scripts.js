// ===============================
// SMARTCARGO-AIPA Frontend Controller
// ===============================

const form = document.getElementById("formCargo");
const semaforoStatus = document.getElementById("semaforoStatus");
const documentsList = document.getElementById("documentsList");
const advisorBox = document.getElementById("advisor");
const explanationBox = document.getElementById("explanation");

const resetBtn = document.getElementById("resetForm");
const printBtn = document.getElementById("printPDF");
const whatsappBtn = document.getElementById("shareWhatsApp");
const translateBtn = document.getElementById("translateBtn");

const lengthInput = document.getElementById("length_cm");
const widthInput = document.getElementById("width_cm");
const heightInput = document.getElementById("height_cm");
const volumeInput = document.getElementById("volume");
const roleSelect = document.getElementById("roleSelect");

let currentLang = "en"; // default English

// ===============================
// Calculate Volume
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
// Role-based UI adaptation
// ===============================
function adaptUIForRole(role) {
    // Show/hide fields or change labels according to role
    // Example: Shipper sees all document requirements
    // Warehouse sees only documents from forwarder/driver
    // Operador sees full review screen
    // Here you can implement additional dynamic adaptations
}

roleSelect.addEventListener("change", (e) => adaptUIForRole(e.target.value));

// ===============================
// Translate EN ⇄ ES
// ===============================
translateBtn.addEventListener("click", () => {
    currentLang = currentLang === "en" ? "es" : "en";
    document.querySelectorAll("[data-en][data-es]").forEach(el => {
        el.textContent = currentLang === "en" ? el.getAttribute("data-en") : el.getAttribute("data-es");
    });
});

// ===============================
// Form submit
// ===============================
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    semaforoStatus.textContent = "PROCESSING…";
    advisorBox.textContent = "";
    explanationBox.textContent = "";
    documentsList.innerHTML = "";

    const formData = new FormData(form);

    const docsFiles = document.getElementById("documents").files;
    const docsArray = [];
    for (let i = 0; i < docsFiles.length; i++) {
        docsArray.push({ filename: docsFiles[i].name, description: docsFiles[i].name });
    }

    const payload = new FormData();
    payload.append("mawb", formData.get("mawb"));
    payload.append("hawb", formData.get("hawb"));
    payload.append("origin", formData.get("origin"));
    payload.append("destination", formData.get("destination"));
    payload.append("cargo_type", formData.get("cargo_type"));
    payload.append("flight_date", formData.get("flight_date"));
    payload.append("weight_kg", formData.get("weight_kg"));
    payload.append("length_cm", formData.get("length_cm"));
    payload.append("width_cm", formData.get("width_cm"));
    payload.append("height_cm", formData.get("height_cm"));
    payload.append("role", formData.get("role"));
    payload.append("documents_json", JSON.stringify(docsArray));

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            body: payload
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Validation error");

        // Render results
        semaforoStatus.textContent = data.semaforo;
        explanationBox.textContent = data.explanation || "";
        advisorBox.textContent = data.advisor || "";

        if (data.documents_required) {
            let html = "<ul>";
            data.documents_required.forEach(doc => {
                const missing = data.missing_docs.includes(doc) ? "❌" : "✅";
                html += `<li>${doc} ${missing}</li>`;
            });
            html += "</ul>";
            documentsList.innerHTML = html;
        }

    } catch (err) {
        semaforoStatus.textContent = "🔴 NOT ACCEPTABLE";
        explanationBox.textContent = err.message;
    }
});

// ===============================
// Reset form
// ===============================
resetBtn.addEventListener("click", () => {
    form.reset();
    semaforoStatus.textContent = "-";
    documentsList.innerHTML = "";
    advisorBox.textContent = "";
    explanationBox.textContent = "";
});

// ===============================
// Print / PDF
// ===============================
printBtn.addEventListener("click", () => {
    window.print();
});

// ===============================
// WhatsApp share
// ===============================
whatsappBtn.addEventListener("click", () => {
    const message =
`SMARTCARGO-AIPA by May Roga LLC
Result: ${semaforoStatus.textContent}
Explanation: ${explanationBox.textContent}
Advisor: ${advisorBox.textContent}`;
    const url = "https://api.whatsapp.com/send?text=" + encodeURIComponent(message);
    window.open(url, "_blank");
});
