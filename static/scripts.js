let lang = "en";

function goStep2() {
  document.getElementById("page1").classList.add("hidden");
  document.getElementById("page2").classList.remove("hidden");
}

function validate() {
  const data = new FormData();
  [
    "mawb","hawb","role","origin","destination",
    "cargo_type","weight","length","width","height","dot"
  ].forEach(id => data.append(id, document.getElementById(id).value));

  fetch("/validate", { method:"POST", body:data })
    .then(r => r.json())
    .then(showResult);
}

function showResult(res) {
  document.getElementById("page2").classList.add("hidden");
  document.getElementById("result").classList.remove("hidden");

  const map = {
    GREEN:"🟢 ACCEPTABLE",
    YELLOW:"🟡 CONDITIONAL",
    RED:"🔴 NOT ACCEPTABLE"
  };

  document.getElementById("semaforo").innerText = map[res.status];
  document.getElementById("analysis").innerText =
    res.analysis + "\n\n" + res.disclaimer;
}

function sendWhatsApp() {
  const text = document.getElementById("analysis").innerText;
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`);
}

function toggleLang() {
  if (lang === "en") {
    document.querySelector("h3").innerText = "Registrar / Validar Carga";
    lang = "es";
  } else {
    location.reload();
  }
}
