// ================= VALIDATE =================

function validate() {
  const data = new FormData();
  data.append("role", document.getElementById("role").value);
  data.append("lang", document.getElementById("lang").value);
  data.append("dossier", document.getElementById("dossier").value);

  fetch("/validate", { method: "POST", body: data })
    .then(r => r.json())
    .then(showResult)
    .catch(() => {
      alert("System error. Please try again.");
    });
}

function showResult(res) {
  const resultBox = document.getElementById("result");
  const semaforo = document.getElementById("semaforo");
  const analysis = document.getElementById("analysis");
  const legal = document.getElementById("legal");

  resultBox.classList.remove("hidden");

  semaforo.className = "";
  if (res.status === "GREEN") {
    semaforo.innerText = "ACCEPTABLE";
    semaforo.classList.add("semaforo-green");
  } else if (res.status === "YELLOW") {
    semaforo.innerText = "CONDITIONAL";
    semaforo.classList.add("semaforo-yellow");
  } else {
    semaforo.innerText = "NOT ACCEPTABLE";
    semaforo.classList.add("semaforo-red");
  }

  analysis.innerText = res.analysis;
  legal.innerText = res.legal_notice;
}

// ================= VOICE =================

function speak() {
  const text = document.getElementById("analysis").innerText;
  if (!text) return;

  const lang = document.getElementById("lang").value;
  const msg = new SpeechSynthesisUtterance(text);

  msg.lang = lang === "Spanish" ? "es-ES" : "en-US";
  msg.rate = 0.95;
  msg.pitch = 1;

  speechSynthesis.cancel();
  speechSynthesis.speak(msg);
}

// ================= ADMIN =================

function adminAsk() {
  const data = new FormData();
  data.append("username", document.getElementById("adminUser").value);
  data.append("password", document.getElementById("adminPass").value);
  data.append("question", document.getElementById("adminQ").value);

  fetch("/admin", { method: "POST", body: data })
    .then(r => r.json())
    .then(r => {
      document.getElementById("adminAnswer").innerText =
        r.answer || "Unauthorized access";
    });
}

// ================= LANG SWITCH =================

function switchLang() {
  const lang = document.getElementById("lang").value;

  document.getElementById("roleLabel").innerText =
    lang === "Spanish" ? "Rol" : "Role";

  document.getElementById("dossier").placeholder =
    lang === "Spanish"
      ? "Pegue aquí toda la documentación revisada en counter"
      : "Paste here the complete documentation reviewed at counter";

  document.getElementById("validateBtn").innerText =
    lang === "Spanish" ? "Validar Carga" : "Validate Cargo";

  document.getElementById("continueBtn").innerText =
    lang === "Spanish" ? "Continuar" : "Continue";
}
