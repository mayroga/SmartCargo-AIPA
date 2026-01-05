const translations = {
    en: {
        act: "1. Service Activation",
        sol: "2. Solution Center",
        l_desc: "PRIVATE ADVISORS. Not IATA/TSA/DOT. Technical solutions to prevent financial loss."
    },
    es: {
        act: "1. Activación de Servicio",
        sol: "2. Centro de Soluciones",
        l_desc: "ASESORES PRIVADOS. No somos IATA/TSA/DOT. Soluciones técnicas para evitar pérdidas de dinero."
    }
};

let timer;

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations.en;
    document.getElementById("t_act").innerText = t.act;
    document.getElementById("t_sol").innerText = t.sol;
}

function previewImages() {
    const container = document.getElementById("previewContainer");
    const files = document.getElementById("fileInput").files;
    container.innerHTML = "";
    Array.from(files).forEach(file => {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.className = "preview-img";
        container.appendChild(img);
    });
}

function clearForm() {
    document.getElementById("promptField").value = "";
    document.getElementById("fileInput").value = "";
    document.getElementById("previewContainer").innerHTML = "";
    document.getElementById("advResponse").innerHTML = "";
    document.getElementById("actionBtns").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
    }

    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const user = prompt("ADMIN USER:");
        const pass = user ? prompt("ADMIN PASS:") : null;

        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(user) fd.append("user", user); if(pass) fd.append("password", pass);

        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<h4>🔍 AUDITING TECHNICAL COMPLIANCE...</h4>";
        
        const fd = new FormData(e.target);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `<div id="report" class="report-box">
                <h3 style="color:#01579b; margin-top:0;">AUDIT & ACTION PLAN</h3>
                <p style="white-space: pre-wrap;">${data.data}</p>
            </div>`;
            document.getElementById("actionBtns").style.display = "flex";
            startTimer();
        } catch (err) { out.innerHTML = "Connection Error."; }
    };
});

function startTimer() {
    const box = document.getElementById("timerBox");
    box.style.display = "block";
    let timeLeft = 300;
    clearInterval(timer);
    timer = setInterval(() => {
        timeLeft--;
        document.getElementById("secs").innerText = timeLeft;
        if(timeLeft <= 0) location.reload();
    }, 1000);
}

function downloadPDF() { html2pdf().from(document.getElementById("report")).save("SmartCargo_Plan.pdf"); }
function shareWA() {
    const text = document.getElementById("report").innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}
