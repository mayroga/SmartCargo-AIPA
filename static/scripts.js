const form = document.getElementById("formCargo");
const semaforoStatus = document.getElementById("semaforoStatus");
const documentsList = document.getElementById("documentsList");
const advisor = document.getElementById("advisor");
const translateBtn = document.getElementById("translateBtn");

let isEnglish = true;

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const cargoData = {
        mawb: formData.get("mawb"),
        hawb: formData.get("hawb"),
        origin: formData.get("origin"),
        destination: formData.get("destination"),
        cargo_type: formData.get("cargo_type"),
        flight_date: formData.get("flight_date"),
        weight_kg: parseFloat(formData.get("weight_kg")),
        volume: parseFloat(formData.get("volume")),
        length_cm: parseFloat(formData.get("length_cm")),
        width_cm: parseFloat(formData.get("width_cm")),
        height_cm: parseFloat(formData.get("height_cm")),
        role: formData.get("role"),
        documents: Array.from(formData.getAll("documents")).map(f => f.name)
    };

    const res = await fetch("/cargo/validate", {
        method: "POST",
        body: JSON.stringify(cargoData),
        headers: {"Content-Type": "application/json"}
    });

    const data = await res.json();
    displayResults(data);
});

function displayResults(data) {
    semaforoStatus.textContent = data.semaforo;
    documentsList.innerHTML = "<strong>Documents:</strong> " + (data.documents || []).join(", ");
    advisor.textContent = "Advisor: " + (data.advisor || "");
}

document.getElementById("resetForm").addEventListener("click", () => {
    form.reset();
    semaforoStatus.textContent = "-";
    documentsList.innerHTML = "Documents:";
    advisor.textContent = "Advisor:";
});

document.getElementById("printPDF").addEventListener("click", () => {
    window.print();
});

document.getElementById("shareWhatsApp").addEventListener("click", () => {
    const url = "https://api.whatsapp.com/send?text=" + encodeURIComponent(
        `Cargo Validation Results:\nSemáforo: ${semaforoStatus.textContent}\nDocuments: ${documentsList.textContent}\nAdvisor: ${advisor.textContent}`
    );
    window.open(url, "_blank");
});

translateBtn.addEventListener("click", () => {
    isEnglish = !isEnglish;
    document.querySelectorAll("label, button, h1, h2, p").forEach(el => {
        if (el.dataset.en && el.dataset.es) {
            el.textContent = isEnglish ? el.dataset.en : el.dataset.es;
        }
    });
});
