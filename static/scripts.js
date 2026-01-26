function validate() {
  const data = new FormData();
  data.append("role", document.getElementById("role").value);
  data.append("lang", "English");
  data.append("dossier", document.getElementById("dossier").value);

  const photos = document.getElementById("photos").files;
  for (let i = 0; i < photos.length; i++) {
    data.append("files", photos[i]);
  }

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
