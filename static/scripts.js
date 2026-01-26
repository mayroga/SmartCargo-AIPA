// ---------------- VALIDATE ----------------
function validate() {
  const data = new FormData();
  data.append("role", document.getElementById("role").value);
  data.append("lang", document.getElementById("lang").value);
  data.append("dossier", document.getElementById("dossier").value);

  fetch("/validate", { method: "POST", body: data })
    .then(r => r.json())
    .then(showResult);
}

function showResult(res) {
  document.getElementById("result").classList.remove("hidden");

  const semaforo = document.getElementById("semaforo");
  semaforo.innerText =
    res.status === "GREEN" ? "🟢 ACCEPTABLE" :
    res.status === "YELLOW" ? "🟡 CONDITIONAL" :
    "🔴 NOT ACCEPTABLE";

  semaforo.style.color =
    res.status === "GREEN" ? "green" :
    res.status === "YELLOW" ? "orange" :
    "red";

  document.getElementById("analysis").innerText =
    res.analysis + "\n\n" + res.disclaimer;
}

// ---------------- VOICE ----------------
function speak() {
  const text = document.getElementById("analysis").innerText;
  if (!text) return;

  const msg = new SpeechSynthesisUtterance(text);
  msg.lang = document.getElementById("lang").value === "Spanish" ? "es-ES" : "en-US";
  speechSynthesis.speak(msg);
}

// ---------------- ADMIN ----------------
function adminAsk() {
  const data = new FormData();
  data.append("username", document.getElementById("adminUser").value);
  data.append("password", document.getElementById("adminPass").value);
  data.append("question", document.getElementById("adminQ").value);

  fetch("/admin", { method: "POST", body: data })
    .then(r => r.json())
    .then(r => {
      document.getElementById("adminAnswer").innerText =
        r.answer || "Unauthorized";
    });
}

// ---------------- LANG SWITCH ----------------
function switchLang() {
  const lang = document.getElementById("lang").value;

  document.getElementById("roleLabel").innerText =
    lang === "Spanish" ? "Rol" : "Role";

  document.getElementById("dossier").placeholder =
    lang === "Spanish"
      ? "Pegue aquí toda la documentación revisada en counter"
      : "Paste here the FULL documentation reviewed at counter";

  document.getElementById("validateBtn").innerText =
    lang === "Spanish" ? "Validar Carga" : "Validate Cargo";

  document.getElementById("continueBtn").innerText =
    lang === "Spanish" ? "Continuar" : "Continue";
}
