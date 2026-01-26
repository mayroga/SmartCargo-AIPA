let currentLang = "en";

function toggleLang() {
  if (currentLang === "en") {
    currentLang = "es";
    document.querySelector("#langBtn").innerText = "English";
    document.querySelector("h2").innerText = "SMARTCARGO-AIPA por May Roga LLC";
    document.querySelector("p").innerText = "Sistema Preventivo de Validación Documental · No reemplaza decisiones de aerolínea";
    document.querySelector("[data-i18n='step1']").innerText = "Registrar / Validar Carga";
  } else {
    currentLang = "en";
    document.querySelector("#langBtn").innerText = "Español";
    document.querySelector("h2").innerText = "SMARTCARGO-AIPA by May Roga LLC";
    document.querySelector("p").innerText = "Preventive Documentary Validation System · Does not replace airline decisions";
    document.querySelector("[data-i18n='step1']").innerText = "Register / Validate Cargo";
  }
}

function goStep2() {
  const mawb = document.querySelector("#mawb").value;
  const hawb = document.querySelector("#hawb").value;
  const role = document.querySelector("#role").value;
  if (!mawb || !hawb) { alert("Please fill MAWB & HAWB"); return; }
  document.querySelector("#page1").classList.add("hidden");
  document.querySelector("#page2").classList.remove("hidden");
}

async function validateCargo() {
  const data = new FormData();
  data.append("mawb", document.querySelector("#mawb").value);
  data.append("hawb", document.querySelector("#hawb").value);
  data.append("role", document.querySelector("#role").value);
  data.append("origin", document.querySelector("#origin").value);
  data.append("destination", document.querySelector("#destination").value);
  data.append("cargo_type", document.querySelector("#cargo_type").value);
  data.append("weight", document.querySelector("#weight").value);
  data.append("length", document.querySelector("#length").value);
  data.append("width", document.querySelector("#width").value);
  data.append("height", document.querySelector("#height").value);
  data.append("dot", document.querySelector("#dot").value);

  const resp = await fetch("/validate", { method: "POST", body: data });
  const json = await resp.json();

  document.querySelector("#page2").classList.add("hidden");
  document.querySelector("#result").classList.remove("hidden");
  document.querySelector("#semaforo").innerText = json.semaforo;
  document.querySelector("#analysis").innerText = json.advisor + "\n\n" + json.legal_notice;
}

function sendWhatsApp() {
  const analysis = document.querySelector("#analysis").innerText;
  const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(analysis)}`;
  window.open(url, "_blank");
}
