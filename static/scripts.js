const loginForm = document.getElementById("login-form");
const loginSection = document.getElementById("login-section");
const mainSection = document.getElementById("main-section");
const loginError = document.getElementById("login-error");

let authData = {};

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Guardamos credenciales para enviar en todas las requests
    authData = { username, password };

    // Test simple de auth
    const res = await fetch("/cargo/list_all", {
        method: "GET",
        headers: new Headers({ "Authorization": "Basic " + btoa(username + ":" + password) })
    });

    if (res.status === 401) {
        loginError.textContent = "Usuario o clave incorrectos";
    } else {
        loginSection.classList.add("hidden");
        mainSection.classList.remove("hidden");
    }
});

const cargoForm = document.getElementById("cargo-form");
cargoForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(cargoForm);
    formData.append("username", authData.username);
    formData.append("password", authData.password);

    const files = cargoForm.querySelector('input[type="file"]').files;
    for (let f of files) {
        formData.append("files", f);
    }

    const res = await fetch("/cargo/validate", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    displayResult(data);
});

document.getElementById("reset-btn").addEventListener("click", () => {
    cargoForm.reset();
    document.getElementById("semaphore-display").innerHTML = "";
    document.getElementById("documents-status").innerHTML = "";
    document.getElementById("advisor-msg").innerHTML = "";
});

document.getElementById("print-btn").addEventListener("click", () => {
    window.print();
});

document.getElementById("whatsapp-btn").addEventListener("click", () => {
    const msg = document.getElementById("advisor-msg").innerText;
    const url = `https://wa.me/?text=${encodeURIComponent(msg)}`;
    window.open(url, "_blank");
});

function displayResult(data) {
    document.getElementById("semaphore-display").innerHTML = `<h2>Semáforo: ${data.semaphore}</h2>`;
    let docsHTML = "<ul>";
    if (data.documents) {
        for (let doc of data.documents) {
            docsHTML += `<li>${doc.doc_type}: ${doc.status} ${doc.observation ? "- " + doc.observation : ""}</li>`;
        }
    }
    docsHTML += "</ul>";
    document.getElementById("documents-status").innerHTML = `<h3>Documentos</h3>${docsHTML}`;

    document.getElementById("advisor-msg").innerHTML = `<h3>Asesor</h3><pre>${data.advisor}</pre>`;
    document.getElementById("legal-msg").innerHTML = `<p>${data.legal}</p>`;
}
