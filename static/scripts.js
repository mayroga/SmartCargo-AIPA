function validate() {
  const data = new FormData();
  data.append("role", role.value);
  data.append("lang", lang.value);
  data.append("dossier", dossier.value);

  fetch("/validate", { method: "POST", body: data })
    .then(r => r.json())
    .then(showResult);
}

function highlight(text) {
  const keywords = [
    "review","verify","check","recommend","recommendation",
    "should","must","ensure","required","warning",
    "verificar","revisar","comprobar","recomend",
    "debe","asegurar","advertencia"
  ];

  let output = text;
  keywords.forEach(k => {
    const re = new RegExp(`(${k})`, "gi");
    output = output.replace(re, `<span class="blue">$1</span>`);
  });

  return output;
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

  analysis.innerHTML = highlight(
    res.analysis + "\n\n" + res.disclaimer
  );
}

function clearAll() {
  dossier.value = "";
  analysis.innerHTML = "";
  result.classList.add("hidden");
}

function speak() {
  const text = analysis.innerText;
  if (!text) return;

  const msg = new SpeechSynthesisUtterance(text);
  msg.lang = lang.value === "Spanish" ? "es-ES" : "en-US";
  speechSynthesis.speak(msg);
}

function adminAsk() {
  const data = new FormData();
  data.append("username", adminUser.value);
  data.append("password", adminPass.value);
  data.append("question", adminQ.value);

  fetch("/admin", { method: "POST", body: data })
    .then(r => r.json())
    .then(r => {
      adminAnswer.innerText = r.answer || "Unauthorized";
    });
}

function switchLang() {
  roleLabel.innerText = lang.value === "Spanish" ? "Rol" : "Role";

  dossier.placeholder =
    lang.value === "Spanish"
      ? "Pegue aquí toda la documentación revisada en counter"
      : "Paste here the FULL documentation reviewed at counter";

  validateBtn.innerText =
    lang.value === "Spanish" ? "Validar Carga" : "Validate Cargo";
}
