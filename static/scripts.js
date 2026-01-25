// scripts.js – SmartCargo-AIPA (PRODUCCIÓN)

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    loadCargos();
});

// =======================
// VALIDAR CARGA
// =======================
const cargoForm = document.getElementById("cargoForm");

if (cargoForm) {
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
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (!res.ok) {
                alert("⚠️ Error de validación:\n" + (data.detail || "Datos incompletos"));
                return;
            }

            renderValidationResult(data);
            loadDashboard();
            loadCargos();

        } catch (err) {
            alert("❌ Error de conexión con el servidor");
            console.error(err);
        }
    });
}

// =======================
// DASHBOARD
// =======================
async function loadDashboard() {
    const res = await fetch("/cargo/list_all");
    const cargos = await res.json();

    document.getElementById("total-awb").textContent = cargos.length;
    document.getElementById("ok-count").textContent =
        cargos.filter(c => c.semaphore === "OK").length;
    document.getElementById("warn-count").textContent =
        cargos.filter(c => c.semaphore === "REVISAR").length;
    document.getElementById("crit-count").textContent =
        cargos.filter(c => c.semaphore === "BLOQUEADO").length;
}

// =======================
// TABLA DOCUMENTAL
// =======================
async function loadCargos() {
    const tbody = document.querySelector("#cargoTable tbody");
    tbody.innerHTML = "";

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
            tbody.appendChild(tr);
        });
    });
}

// =======================
function statusClass(status) {
    if (status === "Aprobado") return "ok";
    if (status === "Observación") return "warn";
    return "crit";
}

// =======================
function renderValidationResult(data) {
    alert(
        `Resultado: ${data.semaphore}\n` +
        data.documents.map(d => `${d.doc_type}: ${d.status}`).join("\n")
    );
}
