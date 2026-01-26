let lang = "en";

// ====== Navegación ======
function goStep2() {
    document.getElementById("page1").classList.add("hidden");
    document.getElementById("page2").classList.remove("hidden");
}

function restart() {
    document.getElementById("page2").classList.add("hidden");
    document.getElementById("result").classList.add("hidden");
    document.getElementById("page1").classList.remove("hidden");
    document.getElementById("mawb").value = "";
    document.getElementById("hawb").value = "";
}

// ====== Validación y subida ======
function validate() {
    const data = new FormData();
    const fields = ["mawb","hawb","role","origin","destination","cargo_type","weight","length","width","height","dot"];
    fields.forEach(id => data.append(id, document.getElementById(id).value));

    // fotos
    const photos = document.getElementById("photos").files;
    for (let i=0; i<photos.length && i<3; i++) {
        data.append("files", photos[i]);
    }

    fetch("/validate", {method:"POST", body:data})
    .then(r => r.json())
    .then(showResult)
    .catch(err => alert("Error connecting to server: " + err));
}

// ====== Mostrar resultados ======
function showResult(res) {
    document.getElementById("page2").classList.add("hidden");
    document.getElementById("result").classList.remove("hidden");

    const map = {
        GREEN: "🟢 ACCEPTABLE",
        RED: "🔴 NOT ACCEPTABLE"
    };
    document.getElementById("semaforo").innerText = map[res.status];
    document.getElementById("analysis").innerText = res.ai_advisor;
    
    let issuesHTML = "";
    if (res.issues && res.issues.length > 0) {
        issuesHTML = "Technical Issues:\n" + res.issues.join("\n");
    }
    document.getElementById("issues").innerText = issuesHTML;
}

// ====== WhatsApp ======
function sendWhatsApp() {
    const text = document.getElementById("analysis").innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`);
}

// ====== Texto a voz ======
function speakResult() {
    const msg = new SpeechSynthesisUtterance(document.getElementById("analysis").innerText);
    window.speechSynthesis.speak(msg);
}

// ====== Idioma ======
function toggleLang() {
    if (lang === "en") {
        document.querySelector("h3").innerText = "Registrar / Validar Carga";
        document.querySelector("h2").innerText = "SMARTCARGO-AIPA";
        lang = "es";
    } else {
        location.reload();
    }
}
