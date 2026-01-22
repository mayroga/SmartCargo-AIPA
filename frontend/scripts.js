const form = document.getElementById("cargoForm");
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = new FormData(form);
    const res = await fetch("/cargo/create", { method: "POST", body: data });
    const json = await res.json();
    document.getElementById("status").innerText = `Cargo creado con ID: ${json.cargo_id}`;
});
