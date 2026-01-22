document.addEventListener("DOMContentLoaded", () => {
    loadCargos();

    const form = document.getElementById("createCargoForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(form);

        try {
            const res = await fetch("/cargo/create", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (res.ok) {
                alert(`Cargo creado correctamente. ID: ${data.cargo_id}`);
                form.reset();
                loadCargos();
            } else {
                alert(`Error: ${data.detail || JSON.stringify(data)}`);
            }
        } catch (err) {
            alert(`Error de red: ${err}`);
        }
    });
});

// Cargar todos los cargos y documentos
async function loadCargos() {
    const tbody = document.getElementById("cargoTable");
    tbody.innerHTML = "";

    try {
        // Aquí deberíamos tener un endpoint que liste todos los cargos
        const cargosRes = await fetch("/cargo/listall"); // Crear endpoint /cargo/listall
        const cargosData = await cargosRes.json();

        for (const cargo of cargosData) {
            const docsRes = await fetch(`/cargo/list/${cargo.id}`);
            const docsData = await docsRes.json();
            const docsHTML = docsData.documents.length
                ? docsData.documents.map(d => `<li>${d}</li>`).join("")
                : "<li>No hay documentos</li>";

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${cargo.id}</td>
                <td>${cargo.mawb}</td>
                <td>${cargo.hawb || "-"}</td>
                <td>${cargo.origin}</td>
                <td>${cargo.destination}</td>
                <td>${cargo.cargo_type}</td>
                <td>${new Date(cargo.flight_date).toLocaleDateString()}</td>
                <td><ul>${docsHTML}</ul></td>
            `;
            tbody.appendChild(row);
        }
    } catch (err) {
        console.error("Error cargando los cargos:", err);
    }
}
