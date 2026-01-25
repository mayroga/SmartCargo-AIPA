const form = document.getElementById("cargoForm");
const resultBox = document.getElementById("result");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    const res = await fetch("/cargo/validate", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    resultBox.textContent =
        data.semaphore + "\n\n" +
        "Motivos:\n" + (data.motivos.join("\n") || "Ninguno") + "\n\n" +
        "Asesor SmartCargo-AIPA:\n" + data.advisor + "\n\n" +
        data.legal;
});
