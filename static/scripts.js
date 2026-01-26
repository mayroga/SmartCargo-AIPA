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
  document.getElementById("semaforo").innerText =
    res.status === "GREEN" ? "🟢 ACCEPTABLE" :
    res.status === "YELLOW" ? "🟡 CONDITIONAL" :
    "🔴 NOT ACCEPTABLE";

  document.getElementById("analysis").innerText =
    res.analysis + "\n\n" + res.disclaimer;
}

function speak() {
  const msg = new SpeechSynthesisUtterance(
    document.getElementById("analysis").innerText
  );
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
  document.getElementById("roleLabel").innerText = lang === "Spanish" ? "Rol" : "Role";
  document.getElementById("dossier").placeholder = lang === "Spanish" ?
    "Pega aquí el archivo documental completo revisado en counter" :
    "Paste FULL documentary file reviewed at counter";
  document.getElementById("validateBtn").innerText = lang === "Spanish" ?
    "Validar Carga" : "Validate Cargo";
  document.getElementById("continueBtn").innerText = lang === "Spanish" ?
    "Continuar" : "Continue";
}
