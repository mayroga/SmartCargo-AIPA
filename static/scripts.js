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
    res.status === "YELLOW" ? "orange" :
    "red";

  const combined = res.analysis + "\n\n" + res.disclaimer;
  analysis.innerHTML = highlightSuggestions(combined);
}

/* 🔵 Highlight VERIFY / CHECK / REVIEW */
function highlightSuggestions(text) {
  return text
    .replace(/(verify|verification|check|review|corregir|revisar|verificar)/gi,
      '<span class="blue">$1</span>')
    .replace(/\n/g, "<br>");
}

/* 🔊 VOICE */
function speak() {
  const msg = new SpeechSynthesisUtterance(analysis.innerText);
  msg.lang = lang.value === "Spanish" ? "es-ES" : "en-US";
  speechSynthesis.speak(msg);
}

/* 📲 WHATSAPP */
function sendWhatsApp() {
  const text = encodeURIComponent(analysis.innerText);
  window.open(`https://wa.me/?text=${text}`, "_blank");
}

/* 🧹 CLEAR */
function clearAll() {
  dossier.value = "";
  result.classList.add("hidden");
  analysis.innerHTML = "";
}

/* 🌐 LANG */
function switchLang() {
  roleLabel.innerText = lang.value === "Spanish" ? "Rol" : "Role";
  dossier.placeholder = lang.value === "Spanish"
    ? "Pegue aquí toda la documentación revisada en counter"
    : "Paste FULL documentation reviewed at counter";
  validateBtn.innerText = lang.value === "Spanish"
    ? "Validar Carga"
    : "Validate Cargo";
}

/* 🔐 ADMIN */
function adminAsk() {
  const data = new FormData();
  data.append("username", adminUser.value);
  data.append("password", adminPass.value);
  data.append("question", adminQ.value);

  fetch("/admin", { method: "POST", body: data })
    .then(r => r.json())
    .then(r => adminAnswer.innerText = r.answer || "Unauthorized");
}
