// scripts.js

document.addEventListener("DOMContentLoaded", () => {
    const createForm = document.getElementById("createCargoForm");
    const cargoTableBody = document.querySelector("#cargoTable tbody");
    const langToggle = document.getElementById("langToggle");
    const printBtn = document.getElementById("printBtn");
    const whatsappBtn = document.getElementById("whatsappBtn");

    let lang = "en";

    // -------------------
    // Crear Cargo
    // -------------------
    createForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(createForm);
        const res = await fetch("/cargo/create", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        alert(data.message);
        loadCargos();
        createForm.reset();
    });

    // -------------------
    // Cargar tabla de cargos
    // -------------------
    async function loadCargos() {
        // Aquí se pueden cargar todos los cargos y sus documentos
        // Ejemplo de dummy:
        const dummyCargo = {
            cargo_id: 1,
            mawb: "729-93133106",
            hawb: "",
            origin: "MIAMI",
            destination: "SAN JOSE",
            type: "SPARE PARTS",
            flight_date: "2025-10-21",
            documents: [
                {doc_type:"Air Waybill", version:"v1", status:"pending", responsible:"admin", upload_date:"2026-01-22", audit_notes:"Revisar AWB físico"},
                {doc_type:"Commercial Invoice", version:"v1", status:"approved", responsible:"admin", upload_date:"2026-01-22", audit_notes:"Factura OK"}
            ]
        };

        cargoTableBody.innerHTML = "";
        dummyCargo.documents.forEach(doc => {
            const row = `<tr>
                <td>${dummyCargo.cargo_id}</td>
                <td>${dummyCargo.mawb}</td>
                <td>${dummyCargo.hawb}</td>
                <td>${dummyCargo.origin}</td>
                <td>${dummyCargo.destination}</td>
                <td>${dummyCargo.type}</td>
                <td>${dummyCargo.flight_date}</td>
                <td>${doc.doc_type}</td>
                <td>${doc.version}</td>
                <td>${doc.status}</td>
                <td>${doc.responsible}</td>
                <td>${doc.upload_date}</td>
                <td>${doc.audit_notes}</td>
                <td><button onclick="alert('Validar / Añadir notas')">Audit</button></td>
            </tr>`;
            cargoTableBody.innerHTML += row;
        });
    }

    loadCargos();

    // -------------------
    // Traducción
    // -------------------
    langToggle.addEventListener("click", () => {
        lang = lang === "en" ? "es" : "en";
        alert(`Language changed to ${lang}`);
        // Aquí se puede agregar traducción de todos los textos
    });

    // -------------------
    // PDF / Imprimir
    // -------------------
    printBtn.addEventListener("click", () => {
        window.print();
    });

    // -------------------
    // WhatsApp
    // -------------------
    whatsappBtn.addEventListener("click", () => {
        const message = "Cargo report: " + dummyCargo.mawb;
        window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(message)}`, "_blank");
    });
});
