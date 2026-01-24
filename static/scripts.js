let lang = "en";

function toggleLang() {
  lang = lang === "en" ? "es" : "en";
  alert(lang === "es" ? "Modo Español" : "English Mode");
}

document.getElementById("cargoForm").onsubmit = async (e) => {
  e.preventDefault();
  const data = new FormData(e.target);
  await fetch("/cargo/create", { method: "POST", body: data });
  loadCargos();
};

async function loadCargos() {
  const res = await fetch("/cargo/all");
  const cargos = await res.json();
  const table = document.getElementById("cargoTable");
  table.innerHTML = "";

  cargos.forEach(c => {
    table.innerHTML += `
      <tr>
        <td>${c.id}</td>
        <td>${c.mawb}</td>
        <td>${c.origin} → ${c.destination}</td>
        <td>${c.documents.length}</td>
        <td><a href="/cargo/report/pdf/${c.id}" target="_blank">PDF</a></td>
        <td>
          <a href="https://wa.me/?text=SmartCargo Advisory MAWB ${c.mawb}" target="_blank">
            WhatsApp
          </a>
        </td>
      </tr>
    `;
  });
}

loadCargos();
