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

        if (!res.ok) throw new Error("Error validando cargo");

        const result = await res.json();
        alert(result.status + "\n" + result.motivos.join("\n"));
        displayCargo(result);
    } catch (err) {
        alert("Error: " + err.message);
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
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>${result.status}</td>
        <td>-</td>
        <td>${new Date().toLocaleDateString()}</td>
        <td>${result.motivos.join(", ")}</td>
    `;
    cargoTableBody.appendChild(row);
}

// -------------------
// Cargar cargos y documentos
// -------------------
async function loadCargos() {
    cargoTableBody.innerHTML = "";
    try {
        const res = await fetch("/cargo/list_all");
        if (!res.ok) throw new Error("No se pudieron cargar los cargos");
        const cargos = await res.json();

        cargos.forEach(cargo => {
            if (!cargo.documents || cargo.documents.length === 0) {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${cargo.id}</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                `;
                cargoTableBody.appendChild(row);
            } else {
                cargo.documents.forEach(doc => {
                    const row = document.createElement("tr");
                    let displayStatus = doc.status;
                    let displayDocs = doc.doc_type;

                    if (currentRole === "owner") {
                        displayDocs = "—";
                    } else if (currentRole === "driver") {
                        displayStatus = doc.status === "pending" ? "🔴 NO" : "🟢 YES";
                    }

                    row.innerHTML = `
                        <td>${cargo.id}</td>
                        <td>${displayDocs}</td>
                        <td>${doc.filename || ""}</td>
                        <td>${doc.version || ""}</td>
                        <td>${displayStatus || ""}</td>
                        <td>${doc.responsible || ""}</td>
                        <td>${doc.upload_date || ""}</td>
                        <td>${doc.audit_notes || ""}</td>
                    `;
                    cargoTableBody.appendChild(row);
                });
            }
        });
    } catch (err) {
        console.error(err);
        cargoTableBody.innerHTML = `<tr><td colspan="8">Error cargando cargos</td></tr>`;
    }
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
    const titles = isSpanish 
        ? ["ID Cargo","Tipo Doc","Archivo","Versión","Estado","Responsable","Fecha Subida","Notas Auditoría"]
        : ["Cargo ID","Doc Type","Filename","Version","Status","Responsible","Upload Date","Audit Notes"];
    headers.forEach((th,i) => th.textContent = titles[i]);

    roleSelect.options[0].text = isSpanish ? "Dueño" : "Owner";
    roleSelect.options[1].text = isSpanish ? "Forwarder / Agente" : "Forwarder / Agent";
    roleSelect.options[2].text = isSpanish ? "Camionero" : "Driver";
    roleSelect.options[3].text = isSpanish ? "Warehouse / Admin" : "Warehouse / Admin";
});

// -------------------
// Imprimir / Export PDF
// -------------------
printBtn.addEventListener("click", () => window.print());

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
