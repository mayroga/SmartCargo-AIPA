// scripts.js – Asesor SmartCargo-AIPA
let isSpanish = true;
let currentRole = "owner";

// ====================
// ELEMENTOS
// ====================
const cargoForm = document.getElementById("cargoForm");
const cargoTableBody = document.querySelector("#cargoTable tbody");
const roleSelect = document.getElementById("roleSelect");
const translateBtn = document.getElementById("translateBtn");

const dashboardLabels = {
    total: document.getElementById("label-total"),
    ok: document.getElementById("label-ok"),
    warn: document.getElementById("label-warn"),
    crit: document.getElementById("label-crit")
};

const thAWB = document.getElementById("th-awb");
const thDoc = document.getElementById("th-doc");
const thStatus = document.getElementById("th-status");
const thObs = document.getElementById("th-observation");
const thNorm = document.getElementById("th-norm");
const subtitle = document.getElementById("subtitle");
const validateBtn = document.getElementById("validateBtn");
const labelRole = document.getElementById("label-role");

// ====================
// VALIDAR CARGA
// ====================
cargoForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        mawb: cargoForm.mawb.value,
        hawb: cargoForm.hawb.value,
        origin: cargoForm.origin.value,
        destination: cargoForm.destination.value,
        cargo_type: cargoForm.cargo_type.value,
        flight_date: cargoForm.flight_date.value
    };

    try {
        const res = await fetch("/cargo/validate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            alert((isSpanish ? "Error de validación:\n" : "Validation error:\n") + (data.detail || "Datos incompletos"));
            return;
        }

        alert(renderValidationMessage(data));
        loadDashboard();
        loadCargos();

    } catch (err) {
        alert(isSpanish ? "Error de conexión con el servidor" : "Server connection error");
        console.error(err);
    }
});

// ====================
// RENDER MENSAJE VALIDACIÓN
// ====================
function renderValidationMessage(data) {
    return (isSpanish ? "Semáforo: " : "Semaphore: ") + data.semaphore + "\n" +
        data.documents.map(d => `${d.doc_type}: ${d.status}`).join("\n");
}

// ====================
// DASHBOARD
// ====================
async function loadDashboard() {
    const res = await fetch("/cargo/list_all");
    const cargos = await res.json();

    document.getElementById("total-awb").textContent = cargos.length;
    document.getElementById("ok-count").textContent = cargos.filter(c => c.semaphore === "OK").length;
    document.getElementById("warn-count").textContent = cargos.filter(c => c.semaphore === "REVISAR").length;
    document.getElementById("crit-count").textContent = cargos.filter(c => c.semaphore === "BLOQUEADO").length;
}

// ====================
// TABLA DOCUMENTAL
// ====================
async function loadCargos() {
    cargoTableBody.innerHTML = "";
    const res = await fetch("/cargo/list_all");
    const cargos = await res.json();

    cargos.forEach(cargo => {
        cargo.documents.forEach(doc => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${cargo.mawb}</td>
                <td>${doc.doc_type}</td>
                <td class="${statusClass(doc.status)}">${doc.status}</td>
                <td>${doc.observation || "—"}</td>
                <td>${doc.norm || "IATA"}</td>
            `;
            cargoTableBody.appendChild(tr);
        });
    });
}

function statusClass(status) {
    if (status === "Aprobado") return "ok";
    if (status === "Observación") return "warn";
    return "crit";
}

// ====================
// CAMBIO DE ROL
// ====================
roleSelect.addEventListener("change", e => {
    currentRole = e.target.value;
    loadCargos();
});

// ====================
// TRADUCCIÓN ESP/ENG
// ====================
translateBtn.addEventListener("click", () => {
    isSpanish = !isSpanish;

    // TITULOS
    document.querySelector("h1").textContent = "Asesor SmartCargo-AIPA";
    subtitle.textContent = isSpanish ? "Validación de Carga y Documentos" : "Cargo & Document Validation";

    // FORMULARIO
    validateBtn.textContent = isSpanish ? "Validar Carga" : "Validate Cargo";
    labelRole.textContent = isSpanish ? "Rol:" : "Role:";

    // ROLES
    roleSelect.options[0].text = isSpanish ? "Dueño" : "Owner";
    roleSelect.options[1].text = isSpanish ? "Forwarder / Agente" : "Forwarder / Agent";
    roleSelect.options[2].text = isSpanish ? "Camionero" : "Driver";
    roleSelect.options[3].text = isSpanish ? "Warehouse / Admin" : "Warehouse / Admin";

    // DASHBOARD
    dashboardLabels.total.textContent = isSpanish ? "Total AWB" : "Total AWB";
    dashboardLabels.ok.textContent = isSpanish ? "Documentos Correctos" : "Documents OK";
    dashboardLabels.warn.textContent = isSpanish ? "En Observación" : "Under Observation";
    dashboardLabels.crit.textContent = isSpanish ? "Críticos" : "Critical";

    // TABLA
    thAWB.textContent = isSpanish ? "AWB" : "AWB";
    thDoc.textContent = isSpanish ? "Documento" : "Document";
    thStatus.textContent = isSpanish ? "Estado" : "Status";
    thObs.textContent = isSpanish ? "Observación" : "Observation";
    thNorm.textContent = isSpanish ? "Norma" : "Norm";
});

// ====================
// CARGA INICIAL
// ====================
loadDashboard();
loadCargos();
