// scripts.js

let currentLang = "en";

// Traducción
const translateBtn = document.getElementById("translateBtn");
translateBtn.addEventListener("click", () => {
    if(currentLang === "en") {
        document.querySelector("h1").innerText = "SMARTCARGO-AIPA por May Roga LLC";
        translateBtn.innerText = "English";
        currentLang = "es";
    } else {
        document.querySelector("h1").innerText = "SMARTCARGO-AIPA by May Roga LLC";
        translateBtn.innerText = "Español";
        currentLang = "en";
    }
});

// Roles
const roleSelect = document.getElementById("roleSelect");
const cargoFormContainer = document.getElementById("cargoFormContainer");

const createFormForRole = (role) => {
    let html = `
    <form id="cargoForm">
        <label>MAWB:</label><input type="text" id="mawb" required><br>
        <label>HAWB:</label><input type="text" id="hawb" required><br>
        <label>Origin:</label><input type="text" id="origin" required><br>
        <label>Destination:</label><input type="text" id="destination" required><br>
        <label>Cargo Type:</label><input type="text" id="cargo_type" required><br>
        <label>Flight Date:</label><input type="date" id="flight_date" required><br>
        <label>Weight (kg):</label><input type="number" id="weight_kg" required><br>
        <label>Length (cm):</label><input type="number" id="length_cm" required><br>
        <label>Width (cm):</label><input type="number" id="width_cm" required><br>
        <label>Height (cm):</label><input type="number" id="height_cm" required><br>
        <label>Upload Documents:</label>
        <input type="file" id="documents" multiple><br>
        <button type="submit">Validate / Validar</button>
    </form>
    `;
    cargoFormContainer.innerHTML = html;

    const form = document.getElementById("cargoForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await submitCargoForm(role);
    });
};

roleSelect.addEventListener("change", () => {
    createFormForRole(roleSelect.value);
});

// Preview documentos
const previewDocuments = (documents) => {
    const previewDiv = document.getElementById("documentsPreview");
    previewDiv.innerHTML = "";
    documents.forEach(doc => {
        const container = document.createElement("div");
        container.style.margin = "10px";
        container.innerHTML = `
            <img src="${doc.url}" style="width:150px;cursor:pointer" onclick="window.open('${doc.url}','_blank')">
            <input type="text" value="${doc.description}" style="width:150px">
        `;
        previewDiv.appendChild(container);
    });
};

// Enviar formulario
const submitCargoForm = async (role) => {
    const mawb = document.getElementById("mawb").value;
    const hawb = document.getElementById("hawb").value;
    const origin = document.getElementById("origin").value;
    const destination = document.getElementById("destination").value;
    const cargo_type = document.getElementById("cargo_type").value;
    const flight_date = document.getElementById("flight_date").value;
    const weight_kg = parseFloat(document.getElementById("weight_kg").value);
    const length_cm = parseFloat(document.getElementById("length_cm").value);
    const width_cm = parseFloat(document.getElementById("width_cm").value);
    const height_cm = parseFloat(document.getElementById("height_cm").value);

    // Archivos
    const files = document.getElementById("documents").files;
    const documentsArray = [];
    for(let file of files){
        // Guardar temporalmente usando endpoint upload
        const formData = new FormData();
        formData.append("cargo_id", 0);
        formData.append("doc_type", file.name);
        formData.append("uploaded_by", role);
        formData.append("file", file);
        const res = await fetch("/cargo/upload_document", {method:"POST", body: formData});
        const json = await res.json();
        documentsArray.push(json);
    }
    previewDocuments(documentsArray);

    // Validación cargo
    const payload = new FormData();
    payload.append("mawb", mawb);
    payload.append("hawb", hawb);
    payload.append("origin", origin);
    payload.append("destination", destination);
    payload.append("cargo_type", cargo_type);
    payload.append("flight_date", flight_date);
    payload.append("weight_kg", weight_kg);
    payload.append("length_cm", length_cm);
    payload.append("width_cm", width_cm);
    payload.append("height_cm", height_cm);
    payload.append("role", role);
    payload.append("documents_json", JSON.stringify(documentsArray));

    const validateRes = await fetch("/cargo/validate", {method:"POST", body: payload});
    const result = await validateRes.json();

    const semaforoDiv = document.getElementById("semaforo");
    if(result.semaforo === "🟢 ACCEPTABLE") semaforoDiv.innerText = "🟢 ACCEPTABLE";
    else if(result.semaforo === "🟡 ACCEPTABLE WITH NOTES") semaforoDiv.innerText = "🟡 ACCEPTABLE WITH NOTES";
    else semaforoDiv.innerText = "🔴 NOT ACCEPTABLE";

    document.getElementById("explanation").innerText = result.explanation;
    document.getElementById("advisorMessage").innerText = result.advisor;
};

// Inicialización
createFormForRole(roleSelect.value);
