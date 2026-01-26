let lang = "en";

function goStep2() {
  document.getElementById("page1").classList.add("hidden");
  document.getElementById("page2").classList.remove("hidden");
}

function validate() {
  const data = new FormData();
  const fileInput = document.getElementById("files");
  for (let i = 0; i < fileInput.files.length; i++) {
    data.append("files", fileInput.files[i]);
  }

  ["mawb","hawb","role","origin","destination",
   "cargo_type","weight","length","width","height","dot"].forEach(id => {
    data.append(id, document.getElementById(id).value);
  });

  fetch("/validate", { method:"POST", body:data })
    .then(r=>r.json())
    .then(showResult);
}

function showResult(res) {
  document.getElementById("page2").classList.add("hidden");
  document.getElementById("result").classList.remove("hidden");
  const map = {GREEN:"🟢 ACCEPTABLE",YELLOW:"🟡 CONDITIONAL",RED:"🔴 NOT ACCEPTABLE"};
  document.getElementById("semaforo").innerText = map[res.status];
  document.getElementById("analysis").innerHTML = res.analysis.replace(/\n/g,"<br>");
}

function sendWhatsApp() {
  const text = document.getElementById("analysis").innerText;
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`);
}

function toggleLang() {
  if (lang === "en") {
    document.querySelector("h3").innerText = "Registrar / Validar Carga";
    document.getElementById("origin").placeholder="Origen";
    document.getElementById("destination").placeholder="Destino";
    document.getElementById("weight").placeholder="Peso kg";
    document.getElementById("length").placeholder="Largo cm";
    document.getElementById("width").placeholder="Ancho cm";
    document.getElementById("height").placeholder="Alto cm";
    lang="es";
  } else {
    location.reload();
  }
}

function readText() {
  const text = document.getElementById("analysis").innerText;
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang==="es"?"es-ES":"en-US";
    speechSynthesis.speak(utterance);
  } else {
    alert("Text-to-speech not supported");
  }
}
