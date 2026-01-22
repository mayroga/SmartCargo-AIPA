document.getElementById("cargoForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    const res = await fetch("/cargo/create", { method: "POST", body: data });
    const json = await res.json();
    document.getElementById("status").innerText = `Cargo creado con ID: ${json.cargo_id}`;
});

document.getElementById("statusForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const cargo_id = form.get("cargo_id");
    const role = form.get("role");
    const res = await fetch(`/cargo/status/${cargo_id}/${role}`);
    const json = await res.json();
    document.getElementById("status").innerText = JSON.stringify(json, null, 2);
});
