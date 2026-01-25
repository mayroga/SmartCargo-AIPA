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
// Crear cargo
// -------------------
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

// -------------------
// Cargar cargos y documentos
// -------------------
async function loadCargos() {
    cargoTableBody.innerHTML = "";

    // Traer todos los cargos
    const res = await fetch("/cargo/list_all");
    const cargos = await res.json();

    cargos.forEach(async cargo => {
        // Obtener documentos de cada cargo
        const docRes = await fetch(`/cargo/list/${cargo.id}`);
        const data = await docRes.json();
        const docs = data.documents || [];

        docs.forEach(doc => {
            const row = document.createElement("tr");
            
            let displayStatus = doc.status;
            let displayDocs = doc.doc_type;

            // Vista según rol
            if (currentRole === "owner") {
                displayDocs = "—";
                displayStatus = doc.status; // Solo ve estado
            } else if (currentRole === "forwarder") {
                displayStatus = doc.status;
            } else if (currentRole === "driver") {
                // Semáforo operativo
                displayStatus = doc.status === "pending" ? "🔴 NO" : "🟢 YES";
            } // admin y warehouse ven todo por defecto

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
    document.querySelector("h1").textContent = isSpanish ? "SmartCargo AIPA" : "SmartCargo AIPA";
    document.querySelector("h2").textContent = isSpanish ? "Gestión de Carga y Documentos" : "Cargo & Document Management";
    cargoForm.querySelector("button").textContent = isSpanish ? "Crear Cargo" : "Create Cargo";
    printBtn.textContent = isSpanish ? "Imprimir / PDF" : "Print / PDF";
    whatsappBtn.textContent = isSpanish ? "Enviar WhatsApp" : "Send WhatsApp";

    // Cambiar encabezados de tabla
    const headers = document.querySelectorAll("#cargoTable thead th");
    if (isSpanish) {
        const titles = ["ID Cargo","Tipo Doc","Archivo","Versión","Estado","Responsable","Fecha Subida","Notas Auditoría"];
        headers.forEach((th,i) => th.textContent = titles[i]);
    } else {
        const titles = ["Cargo ID","Doc Type","Filename","Version","Status","Responsible","Upload Date","Audit Notes"];
        headers.forEach((th,i) => th.textContent = titles[i]);
    }
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
