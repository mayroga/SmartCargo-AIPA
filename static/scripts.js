// scripts.js
const cargoForm = document.getElementById("cargoForm");
const cargoTableBody = document.querySelector("#cargoTable tbody");
const translateBtn = document.getElementById("translateBtn");
const printBtn = document.getElementById("printBtn");
const whatsappBtn = document.getElementById("whatsappBtn");

let isSpanish = false;

// Crear cargo
cargoForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(cargoForm);
    const data = Object.fromEntries(formData.entries());

    const res = await fetch("/cargo/create", {
        method: "POST",
        body: new URLSearchParams(data)
    });

    const result = await res.json();
    alert(result.message);
    cargoForm.reset();
    loadCargos();
});

// Cargar cargos y documentos
async function loadCargos() {
    cargoTableBody.innerHTML = "";
    const res = await fetch("/cargo/list/1"); // Demo: cargo_id=1
    const data = await res.json();
    if (data.documents) {
        data.documents.forEach(doc => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${data.cargo_id}</td>
                <td>${doc.split("_")[0]}</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>${doc}</td>
                <td>✔</td>
                <td>Documento cargado</td>
            `;
            cargoTableBody.appendChild(row);
        });
    }
}

// Traducción inglés/español
translateBtn.addEventListener("click", () => {
    isSpanish = !isSpanish;
    document.querySelector("h2").textContent = isSpanish ? "Gestión de Carga y Documentos" : "Cargo & Document Management";
    cargoForm.querySelector("button").textContent = isSpanish ? "Crear Cargo" : "Create Cargo";
    printBtn.textContent = isSpanish ? "Imprimir / PDF" : "Print / PDF";
    whatsappBtn.textContent = isSpanish ? "Enviar WhatsApp" : "Send WhatsApp";
});

// Imprimir / PDF
printBtn.addEventListener("click", () => window.print());

// WhatsApp
whatsappBtn.addEventListener("click", () => {
    let text = "Cargo & Documents:\n";
    document.querySelectorAll("#cargoTable tbody tr").forEach(row => {
        text += Array.from(row.children).map(td => td.textContent).join(" | ") + "\n";
    });
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank");
});

// Inicial carga
loadCargos();
