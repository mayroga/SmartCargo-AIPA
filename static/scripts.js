let lang = "en";

const translations = {
  es: {
    "Register / Validate Cargo": "Registrar / Validar Carga",
    "Validate": "Validar",
    "Validation Results": "Resultados de Validación",
    "Print / PDF": "Imprimir / PDF",
    "WhatsApp": "WhatsApp"
  }
};

document.getElementById("langToggle").onclick = () => {
  lang = lang === "en" ? "es" : "en";
  document.getElementById("langToggle").innerText = lang === "en" ? "Español" : "English";
  translate();
};

function translate() {
  if (lang !== "es") return;
  document.querySelectorAll("h2, button").forEach(el => {
    if (translations.es[el.innerText]) {
      el.innerText = translations.es[el.innerText];
    }
  });
}

["length","width","height"].forEach(id=>{
  document.getElementById(id).oninput = ()=>{
    const l = +length.value || 0;
    const w = +width.value || 0;
    const h = +height.value || 0;
    volume.value = ((l*w*h)/1000000).toFixed(3);
  };
});

async function validateCargo(){
  const payload = {
    mawb: mawb.value,
    hawb: hawb.value,
    origin: origin.value,
    destination: destination.value,
    date: date.value,
    cargo_type: cargo_type.value,
    weight: +weight.value,
    length: +length.value,
    width: +width.value,
    height: +height.value,
    role: role.value,
    documents: ["AWB"]
  };

  const res = await fetch("/cargo/validate", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(payload)
  });

  const data = await res.json();

  semaphore.innerText = "Semáforo: " + data.status;
  details.innerHTML = `
    <b>Required:</b> ${data.required_documents.join(", ")}<br>
    <b>Missing:</b> ${data.missing_documents.join(", ")}<br>
    <b>Issues:</b> ${data.issues.join("; ")}
  `;
  advisor.innerText = data.advisor;
  legal.innerText = data.legal;
}

function printPDF(){
  window.print();
}

function sendWhatsApp(){
  const text = encodeURIComponent(document.getElementById("results").innerText);
  window.open(`https://wa.me/?text=${text}`);
}
