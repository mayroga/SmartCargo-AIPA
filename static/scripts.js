let lang = "en";

document.getElementById("cargoForm").addEventListener("submit", async e => {
    e.preventDefault();
    const form = new FormData(e.target);
    const res = await fetch("/cargo/validate", { method: "POST", body: form });
    const data = await res.json();
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
});

function resetForm() {
    document.getElementById("cargoForm").reset();
    document.getElementById("result").textContent = "";
}

function translate() {
    lang = lang === "en" ? "es" : "en";
    alert(lang === "es" ? "Idioma cambiado a Español" : "Language switched to English");
}

function sendWhatsApp() {
    const text = encodeURIComponent(document.getElementById("result").textContent);
    window.open(`https://wa.me/?text=${text}`, "_blank");
}
