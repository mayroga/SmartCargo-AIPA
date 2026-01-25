// scripts.js

const cargoForm = document.getElementById("cargoForm");
const cargoTableBody = document.querySelector("#cargoTable tbody");
const translateBtn = document.getElementById("translateBtn");
const printBtn = document.getElementById("printBtn");
const whatsappBtn = document.getElementById("whatsappBtn");
const roleSelect = document.getElementById("roleSelect");

let isSpanish = false;
let currentRole = roleSelect.value || "owner";

// -------------------
// Validar cargo
// -------------------
cargoForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(cargoForm);
    const data = Object.fromEntries(formData.entries());

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            body: new URLSearchParams(data)
        });
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const result = await res.json();
        displayCargo(result);
        alert(`${result.status}\n${result.motivos.join("\n")}`);
    } catch (err) {
        alert(`Error validando cargo: ${err}`);
    }
});

// -------------------
// Mostrar cargo validado en tabla
// -------------------
function displayCargo(result) {
    cargoTableBody.innerHTML = "";

    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${result.cargo_id}</td>
        <td>${result.weight} kg</td>
        <td>${result.volume} m³</td>
        <td>${result.status}</td>
        <td>${result.motivos.join(", ")}</td>
        <td>
            ${Object.entries(result.detalles).map(
                ([doc, status]) => `<b>${doc}:</b> ${status}`
            ).join("<br>")}
        </td>
        <td>${new Date().toLocaleDateString()}</td>
        <td>${result.legal}</td>
    `;
    cargoTableBody.appendChild(row);
}

// -------------------
// Cargar todos los cargos
// -------------------
async function loadCargos() {
    cargoTableBody.innerHTML = "";
    const res = await fetch("/cargo/list_all");
    const cargos = await res.json();

    cargos.forEach(cargo => {
        const row = document.createElement("tr");

        // Determinar semáforo según rol
        let semaforo = "—";
        if (currentRole === "owner" || currentRole === "forwarder") {
            semaforo = cargo.documents.some(d => d.status === "🔴 NO ACEPTABLE") ? "🔴" : "🟢";
        } else if (currentRole === "driver") {
            semaforo = cargo.documents.some(d => d.status === "pending") ? "🔴" : "🟢";
        }

        row.innerHTML = `
            <td>${cargo.id}</td>
            <td>${cargo.weight} kg</td>
            <td>${cargo.volume} m³</td>
            <td>${semaforo}</td>
            <td>${cargo.documents.map(d => d.doc_type).join(", ")}</td>
            <td>${cargo.documents.map(d => d.responsible || "").join(", ")}</td>
            <td>${cargo.flight_date}</td>
            <td>${cargo.documents.map(d => d.audit_notes || "").join(" | ")}</td>
        `;
        cargoTableBody.appendChild(row);
    });
}

// -------------------
// Cambiar rol
// -------------------
roleSelect.addEventListener("change", (e) => {
    currentRole = e.target.value;
    loadCargos();
});

// -------------------
// Traducción Español / Inglés
// -------------------
translateBtn.addEventListener("click", () => {
    isSpanish = !isSpanish;

    document.querySelector("h1").textContent = "SmartCargo AIPA";
    document.querySelector("h2").textContent = isSpanish ? "Validación de Carga y Documentos" : "Cargo & Document Validation";

    cargoForm.querySelector("button").textContent = isSpanish ? "Validar Carga" : "Validate Cargo";
    printBtn.textContent = isSpanish ? "Imprimir / PDF" : "Print / PDF";
    whatsappBtn.textContent = isSpanish ? "Enviar WhatsApp" : "Send WhatsApp";

    const headers = document.querySelectorAll("#cargoTable thead th");
    if (isSpanish) {
        const titles = ["ID Cargo", "Peso", "Volumen", "Semáforo", "Documentos", "Responsable", "Fecha Vuelo", "Alertas / Legal"];
        headers.forEach((th, i) => th.textContent = titles[i]);
    } else {
        const titles = ["Cargo ID", "Weight", "Volume", "Semaphore", "Documents", "Responsible", "Flight Date", "Alerts / Legal"];
        headers.forEach((th, i) => th.textContent = titles[i]);
    }

    // Cambiar roles al idioma correspondiente
    roleSelect.options[0].text = isSpanish ? "Dueño" : "Owner";
    roleSelect.options[1].text = isSpanish ? "Forwarder / Agente" : "Forwarder / Agent";
    roleSelect.options[2].text = isSpanish ? "Camionero" : "Driver";
    roleSelect.options[3].text = isSpanish ? "Warehouse / Admin" : "Warehouse / Admin";
});

// -------------------
// Imprimir / Export PDF
// -------------------
printBtn.addEventListener("click", () => {
    window.print();
});

// -------------------
// Enviar por WhatsApp
// -------------------
whatsappBtn.addEventListener("click", () => {
    let text = isSpanish ? "Carga y Documentos:\n" : "Cargo & Documents:\n";
    document.querySelectorAll("#cargoTable tbody tr").forEach(row => {
        text += Array.from(row.children).map(td => td.textContent).join(" | ") + "\n";
    });
    const url = `https://wa.me/?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank");
});

// -------------------
// Carga inicial
// -------------------
loadCargos();
