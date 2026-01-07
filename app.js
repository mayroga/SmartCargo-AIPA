let imgB64 = "";
let selectedRole = "";

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if(params.get("access") === "granted"){
        document.getElementById("accessSection").style.display = "none";
        document.getElementById("mainApp").style.display = "block";
    }
});

function selRole(role, el){
    selectedRole = role;
    document.querySelectorAll(".role-btn").forEach(b => b.classList.remove("selected"));
    el.classList.add("selected");
}

function loadPhoto(el){
    const r = new FileReader();
    r.onload = e => { imgB64 = e.target.result; alert("Lectura de carga completada."); };
    r.readAsDataURL(el.files[0]);
}

async function pay(amt){
    const fd = new FormData();
    fd.append("amount", amt);
    fd.append("awb", document.getElementById("awb").value || "REF-SMART");
    fd.append("user", document.getElementById("adminUser").value);
    fd.append("password", document.getElementById("adminPass").value);
    const r = await fetch("/create-payment", {method:"POST", body:fd});
    const d = await r.json();
    if(d.url) location.href = d.url;
}

async function analyze(){
    if(!selectedRole) return alert("Seleccione su rol.");
    const out = document.getElementById("advResponse");
    out.style.display = "block";
    out.innerText = "SISTEMA: Procesando millones de variables logísticas...";
    const fd = new FormData();
    fd.append("prompt", `ROL: ${selectedRole}. ${document.getElementById("prompt").value}`);
    fd.append("image_data", imgB64);
    const r = await fetch("/advisory", {method:"POST", body:fd});
    const d = await r.json();
    out.innerText = d.data;
}

function sendWS(){
    window.open("https://wa.me/?text=" + encodeURIComponent(document.getElementById("advResponse").innerText));
}
