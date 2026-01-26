// ===============================
// SMARTCARGO-AIPA by May Roga LLC
// Frontend Dynamic Controller
// ===============================

const form = document.getElementById("formCargo");
const semaforoStatus = document.getElementById("semaforoStatus");
const documentsList = document.getElementById("documentsList");
const advisorBox = document.getElementById("advisor");
const resetBtn = document.getElementById("resetForm");
const printBtn = document.getElementById("printPDF");
const whatsappBtn = document.getElementById("shareWhatsApp");
const translateBtn = document.getElementById("translateBtn");
const roleSelect = document.getElementById("roleSelect");

const lengthInput = form.querySelector("[name=length_cm]");
const widthInput  = form.querySelector("[name=width_cm]");
const heightInput = form.querySelector("[name=height_cm]");
const volumeInput = form.querySelector("[name=volume_cm]") || form.querySelector("[name=volume]");

let currentLang = "en";

// ===============================
// Auto Volume Calculation
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

[lengthInput, widthInput, heightInput].forEach(input => input.addEventListener("input", calculateVolume));

// ===============================
// Role-based dynamic view
// ===============================
roleSelect.addEventListener("change", () => {
    const role = roleSelect.value;
    adjustFormByRole(role);
});

function adjustFormByRole(role) {
    // Oculta/Deshabilita campos según rol
    const editableFields = {
        "Shipper": ["mawb","hawb","origin","destination","cargo_type","flight_date","weight_kg","length_cm","width_cm","height_cm","documents"],
        "Forwarder": ["mawb","hawb","documents"],
        "Chofer": ["mawb","hawb","documents"],
        "Warehouse": ["documents"],
        "Operador": [],
        "Destinatario": []
    };
    const allFields = ["mawb","hawb","origin","destination","cargo_type","flight_date","weight_kg","length_cm","width_cm","height_cm","documents"];
    allFields.forEach(f => {
        const el = form.querySelector(`[name=${f}]`);
        if (!el) return;
        if (editableFields[role].includes(f)) el.disabled = false;
        else el.disabled = true;
    });
}

// ===============================
// Submit Cargo Validation
// ===============================
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    semaforoStatus.textContent = "PROCESSING…";
    advisorBox.textContent = "";
    documentsList.innerHTML = "";

    const formData = new FormData(form);
    const docs = [];
    const files = formData.getAll("documents");
    files.forEach(f => docs.push({filename: f.name}));

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
        volume: Number(formData.get("volume")),
        role: formData.get("role"),
        documents: docs
    };

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            body: JSON.stringify(cargoData),
            headers: {"Content-Type":"application/json"}
        });
        const data = await res.json();
        renderResults(data);
    } catch(err){
        semaforoStatus.textContent="🔴 ERROR";
        advisorBox.textContent=err.message;
    }
});

// ===============================
// Render Results
// ===============================
function renderResults(data){
    semaforoStatus.textContent = data.status || "🔴 NOT ACCEPTABLE";

    let docHtml = "<strong>Documents:</strong><ul>";
    (data.documents_required || []).forEach(doc=>{
        const missing = data.missing_docs && data.missing_docs.includes(doc);
        docHtml += `<li>${doc} ${missing ? "(MISSING)" : "(OK)"}</li>`;
    });
    docHtml += "</ul>";
    documentsList.innerHTML = docHtml;

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
printBtn.addEventListener("click", () => window.print());

// ===============================
// WhatsApp Share
// ===============================
whatsappBtn.addEventListener("click", ()=>{
    const message = `
SMARTCARGO-AIPA by May Roga LLC
Semáforo: ${semaforoStatus.textContent}
Advisor: ${advisorBox.textContent}`;
    window.open("https://api.whatsapp.com/send?text="+encodeURIComponent(message),"_blank");
});

// ===============================
// Translate EN ⇄ ES
// ===============================
translateBtn.addEventListener("click", ()=>{
    currentLang = currentLang==="en"?"es":"en";
    document.querySelectorAll("[data-en][data-es]").forEach(el=>{
        el.textContent = currentLang==="en"?el.getAttribute("data-en"):el.getAttribute("data-es");
    });
});
