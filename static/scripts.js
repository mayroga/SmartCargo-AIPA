let documentsArray = [];
let currentLang = 'en';

function translatePage(lang) {
    currentLang = lang;
    if(lang === 'es') {
        document.getElementById('title').innerText = "SMARTCARGO-AIPA · Sistema Preventivo de Validación Documental";
        document.querySelector('label[for="role"]').innerText = "Seleccione Rol:";
        document.querySelector('#cargoForm label[for="mawb"]').innerText = "MAWB:";
    } else {
        document.getElementById('title').innerText = "SMARTCARGO-AIPA · Preventive Documentary Validation System";
        document.querySelector('label[for="role"]').innerText = "Select Role:";
    }
}

function renderForm() {
    const role = document.getElementById('role').value;
    // Aquí se pueden mostrar/ocultar campos específicos por rol
    console.log("Role selected:", role);
}

document.getElementById('fileUpload').addEventListener('change', function(event) {
    const files = Array.from(event.target.files);
    files.forEach(file => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const div = document.createElement('div');
            div.innerHTML = `
                <img src="${e.target.result}" alt="${file.name}" onclick="zoomImage(this)">
                <input type="text" placeholder="Description" value="${file.name}" onchange="updateDescription(this, '${file.name}')">
            `;
            document.getElementById('docPreview').appendChild(div);
            documentsArray.push({filename: file.name, description: file.name});
        };
        reader.readAsDataURL(file);
    });
});

function updateDescription(input, filename) {
    const doc = documentsArray.find(d => d.filename === filename);
    if(doc) doc.description = input.value;
}

function zoomImage(img) {
    const w = window.open("");
    w.document.write(`<img src="${img.src}" style="width:100%">`);
}

async function validateCargo() {
    const formData = new FormData();
    formData.append("mawb", document.getElementById('mawb').value);
    formData.append("hawb", document.getElementById('hawb').value);
    formData.append("origin", document.getElementById('origin').value);
    formData.append("destination", document.getElementById('destination').value);
    formData.append("cargo_type", document.getElementById('cargo_type').value);
    formData.append("flight_date", document.getElementById('flight_date').value);
    formData.append("weight_kg", parseFloat(document.getElementById('weight_kg').value));
    formData.append("length_cm", parseFloat(document.getElementById('length_cm').value));
    formData.append("width_cm", parseFloat(document.getElementById('width_cm').value));
    formData.append("height_cm", parseFloat(document.getElementById('height_cm').value));
    formData.append("role", document.getElementById('role').value);
    formData.append("documents_json", JSON.stringify(documentsArray));

    const response = await fetch("/cargo/validate", {
        method: "POST",
        body: formData
    });

    if(response.ok) {
        const data = await response.json();
        const semaforoEl = document.getElementById('semaforo');
        if(data.semaforo === "🟢") semaforoEl.style.color = "green";
        else if(data.semaforo === "🟡") semaforoEl.style.color = "orange";
        else semaforoEl.style.color = "red";

        semaforoEl.innerText = `Semáforo: ${data.semaforo}`;
        document.getElementById('validationDetails').innerHTML = `
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;
    } else {
        alert("Error validating cargo");
    }
}
