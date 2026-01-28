function validate() {
  const data = new FormData();
  data.append("role", role.value);
  data.append("lang", lang.value);
  data.append("dossier", dossier.value);

  fetch("/validate", { method: "POST", body: data })
    .then(r => r.json())
    .then(showResult);
}

function showResult(res) {
  result.classList.remove("hidden");

  semaforo.innerText =
    res.status === "GREEN" ? "🟢 ACCEPTABLE" :
    res.status === "YELLOW" ? "🟡 CONDITIONAL" :
    "🔴 NOT ACCEPTABLE";

  semaforo.style.color =
    res.status === "GREEN" ? "green" :
    res.status === "YELLOW" ? "orange" : "red";

  analysis.innerHTML = highlightBlue(
    res.analysis + "\n\n" + res.disclaimer
  );
}

/* 🔵 Highlight VERIFY / CHECK / REVIEW */
function highlightBlue(text) {
  const words = /(verify|verification|check|review|revisar|verificar|comprobar)/gi;
  return text.replace(words, '<span class="blue">$1</span>');
}

/* 🗑 CLEAR */
function clearAll() {
  dossier.value = "";
  result.classList.add("hidden");
  analysis.innerHTML = "";
}

/* 🔊 VOICE */
function speak() {
  const text = analysis.innerText;
  if (!text) return;
  const msg = new SpeechSynthesisUtterance(text);
  msg.lang = lang.value === "Spanish" ? "es-ES" : "en-US";
  speechSynthesis.speak(msg);
}

/* ADMIN */
function adminAsk() {
  const data = new FormData();
  data.append("username", adminUser.value);
  data.append("password", adminPass.value);
  data.append("question", adminQ.value);

  fetch("/admin", { method: "POST", body: data })
    .then(r => r.json())
    .then(r => adminAnswer.innerText = r.answer || "Unauthorized");
}

/* LANG */
function switchLang() {
  roleLabel.innerText = lang.value === "Spanish" ? "Rol" : "Role";
  dossier.placeholder =
    lang.value === "Spanish"
      ? "Pegue aquí toda la documentación revisada en counter"
      : "Paste here the FULL documentation reviewed at counter";
  validateBtn.innerText =
    lang.value === "Spanish" ? "Validar Carga" : "Validate Cargo";
}
