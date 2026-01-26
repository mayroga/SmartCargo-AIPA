// scripts.js

document.addEventListener("DOMContentLoaded", () => {
    const roleSelect = document.getElementById("roleSelect");
    const langSelect = document.getElementById("langSelect");
    const roleSections = document.querySelectorAll(".role-section");
    const validateBtn = document.getElementById("validateBtn");
    const semaforoDiv = document.getElementById("semaforo");
    const documentsDiv = document.getElementById("documents");
    const explanationDiv = document.getElementById("explanation");
    const advisorDiv = document.getElementById("advisor");
    const fileInput = document.getElementById("fileInput");
    const docPreviewContainer = document.getElementById("docPreviewContainer");

    let uploadedDocuments = [];

    // Mostrar formulario según rol
    roleSelect.addEventListener("change", () => {
        roleSections.forEach(s => s.classList.remove("show"));
        const selected = roleSelect.value;
        const section = document.getElementById(selected);
        if(section) section.classList.add("show");
    });

    // Traducir (placeholder)
    langSelect.addEventListener("change", () => {
        const lang = langSelect.value;
        alert("Switching language to: " + lang + " (All labels should translate in production)");
        // Aquí puedes integrar traducción real
    });

    // Preview documentos
    if(fileInput){
        fileInput.addEventListener("change", (e) => {
            docPreviewContainer.innerHTML = "";
            uploadedDocuments = [];
            Array.from(e.target.files).forEach(file => {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    const div = document.createElement("div");
                    div.className = "doc-preview";
                    div.innerHTML = `<img src="${ev.target.result}"><input type="text" value="${file.name}" placeholder="Descripción editable">`;
                    docPreviewContainer.appendChild(div);
                    uploadedDocuments.push({filename: file.name, description: file.name});
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // Validar cargo
    validateBtn.addEventListener("click", async () => {
        const role = roleSelect.value;

        // Solo ejemplo para Shipper
        let payload = {
            mawb: document.getElementById("mawb_shipper")?.value || "",
            hawb: document.getElementById("hawb_shipper")?.value || "",
            origin: document.getElementById("origin_shipper")?.value || "",
            destination: document.getElementById("destination_shipper")?.value || "",
            cargo_type: document.getElementById("cargo_type_shipper")?.value || "",
            flight_date: document.getElementById("flight_date_shipper")?.value || "",
            weight_kg: parseFloat(document.getElementById("weight_shipper")?.value || 0),
            length_cm: parseFloat(document.getElementById("length_shipper")?.value || 0),
            width_cm: parseFloat(document.getElementById("width_shipper")?.value || 0),
            height_cm: parseFloat(document.getElementById("height_shipper")?.value || 0),
            role: role,
            documents_json: JSON.stringify(uploadedDocuments)
        };

        const formData = new FormData();
        for (let key in payload){
            formData.append(key, payload[key]);
        }

        try{
            const response = await fetch("/cargo/validate", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            // Semáforo
            semaforoDiv.textContent = `Semáforo: ${data.semaforo}`;
            if(data.semaforo.includes("🟢")) semaforoDiv.style.color="green";
            else if(data.semaforo.includes("🟡")) semaforoDiv.style.color="orange";
            else semaforoDiv.style.color="red";

            // Documentos
            documentsDiv.innerHTML = `<strong>Required Docs:</strong> ${data.documents_required.join(", ")}<br><strong>Missing Docs:</strong> ${data.missing_docs.join(", ")}`;

            // Explicación
            explanationDiv.innerHTML = `<strong>Explanation:</strong> ${data.explanation}`;

            // Asesor
            advisorDiv.innerHTML = `<strong>Advisor:</strong> ${data.advisor}`;

        } catch(err){
            console.error(err);
            alert("Error validating cargo. Check console.");
        }
    });

});
