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
// Validate Cargo con semáforo operativo
// -------------------
cargoForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(cargoForm);
    const data = Object.fromEntries(formData.entries());

    const res = await fetch("/cargo/validate", {
        method: "POST",
        body: new URLSearchParams(data)
    });

    const result = await res.json();
    alert(`${result.message}\nMotivos:\n- ${result.reasons.join("\n- ")}\n\n${result.legal_note}`);

    loadCargos();
});

// -------------------
// Cargar cargos y documentos
// -------------------
async function loadCargos() {
    cargoTableBody.innerHTML = "";
    const res = await fetch("/cargo/list_all");
    const cargos = await res.json();

    cargos.forEach(async cargo => {
        const docRes = await fetch(`/cargo/list/${cargo.id}`);
        const data = await docRes.json();
        const docs = data.documents || [];

        docs.forEach(doc => {
            const row = document.createElement("tr");
            let displayStatus = doc.status || "Pendiente";
            let displayDocs = doc.doc_type;

            if (currentRole === "owner") displayDocs = "—";
            if (currentRole === "driver") displayStatus = displayStatus === "pending" ? "🔴 NO" : "🟢 YES";

            row.innerHTML = `
                <td>${cargo.id}</td>
                <td>${displayDocs}</td>
                <td>${doc.filename || ""}</td>
                <td>${doc.version || ""}</td>
                <td>${displayStatus}</td>
                <td>${doc.responsible || ""}</td>
                <td>${doc.upload_date || ""}</td>
                <td>${doc.audit_notes || ""}</td>
            `;
            cargoTableBody.appendChild(row);
        });
    });
}

// -------------------
// Cambiar rol
// -------------------
roleSelect.addEventListener("change", e => {
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
    const titles = isSpanish ?
        ["ID Cargo","Tipo Doc","Archivo","Versión","Estado","Responsable","Fecha Subida","Notas Auditoría"] :
        ["Cargo ID","Doc Type","Filename","Version","Status","Responsible","Upload Date","Audit Notes"];
    headers.forEach((th,i)=> th.textContent = titles[i]);

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
// WhatsApp
// -------------------
whatsappBtn.addEventListener("click", () => {
    let text = isSpanish ? "Carga y Documentos:\n" : "Cargo & Documents:\n";
    document.querySelectorAll("#cargoTable tbody tr").forEach(row => {
        text += Array.from(row.children).map(td => td.textContent).join(" | ") + "\n";
    });
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank");
});

// -------------------
// Carga inicial
// -------------------
loadCargos();
