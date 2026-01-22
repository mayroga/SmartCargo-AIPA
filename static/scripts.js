const translations = {
    es: {
        "SmartCargo AIPA": "SmartCargo AIPA",
        "Create Cargo": "Crear Cargo",
        "MAWB": "MAWB",
        "HAWB": "HAWB",
        "Origin": "Origen",
        "Destination": "Destino",
        "Cargo Type": "Tipo de carga",
        "Flight Date": "Fecha de vuelo",
        "Documents": "Documentos",
        "Version": "Versión",
        "Status": "Estado",
        "Responsible": "Responsable",
        "Audit Notes": "Notas de Auditoría"
    },
    en: {
        "Crear Cargo": "Create Cargo",
        "Origen": "Origin",
        "Destino": "Destination",
        "Tipo de carga": "Cargo Type",
        "Fecha de vuelo": "Flight Date",
        "Documentos": "Documents",
        "Versión": "Version",
        "Estado": "Status",
        "Responsable": "Responsible",
        "Notas de Auditoría": "Audit Notes"
    }
};

let currentLang = "en";

function toggleLanguage() {
    currentLang = currentLang === "en" ? "es" : "en";
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        el.innerText = translations[currentLang][key];
    });
}

// Fetch cargos y llenar tabla
async function loadCargos() {
    const tbody = document.querySelector("#cargoTable tbody");
    tbody.innerHTML = "";
    const res = await fetch("/cargo/list/1"); // Ejemplo cargo_id=1
    const data = await res.json();
    if (data.documents) {
        data.documents.forEach(doc => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${data.cargo_id}</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>${doc}</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
            `;
            tbody.appendChild(tr);
        });
    }
}

// Imprimir tabla / generar PDF
function printTable() {
    const printWindow = window.open("", "", "width=900,height=600");
    printWindow.document.write("<html><head><title>Print</title></head><body>");
    printWindow.document.write(document.querySelector("#cargoTable").outerHTML);
    printWindow.document.write("</body></html>");
    printWindow.document.close();
    printWindow.print();
}

// Enviar resumen por WhatsApp
function sendWhatsApp() {
    const tableText = Array.from(document.querySelectorAll("#cargoTable tr"))
        .map(tr => Array.from(tr.cells).map(td => td.innerText).join("\t"))
        .join("\n");
    const phone = prompt("Enter WhatsApp number (with country code):");
    if (phone) {
        const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(tableText)}&phone=${phone}`;
        window.open(url, "_blank");
    }
}

// Inicial
loadCargos();
