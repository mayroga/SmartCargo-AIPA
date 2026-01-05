const translations = {
    en: {
        act: "1. Service Activation",
        sol: "2. Solution Center",
        m_title: "Why SmartCargo?",
        m_desc: "We provide stability to the entire logistics chain. We prevent fines and holds so the paying customer never loses money.",
        l_title: "⚠️ Legal Shield",
        l_desc: "We are PRIVATE ADVISORS. Not IATA/TSA/DOT. We provide technical solutions; we don't certify DG or handle cargo."
    },
    es: {
        act: "1. Activación de Servicio",
        sol: "2. Centro de Soluciones",
        m_title: "¿Por qué SmartCargo?",
        m_desc: "Damos estabilidad a toda la cadena logística. Evitamos multas y retenciones para que el cliente que paga nunca pierda dinero.",
        l_title: "⚠️ Blindaje Legal",
        l_desc: "Somos ASESORES PRIVADOS. No somos IATA/TSA/DOT. Damos soluciones técnicas; no certificamos carga peligrosa ni manipulamos carga."
    }
};

let timer;

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations.en;
    document.getElementById("t_act").innerText = t.act;
    document.getElementById("t_sol").innerText = t.sol;
    document.getElementById("m_title").innerText = t.m_title;
    document.getElementById("m_desc").innerText = t.m_desc;
    document.getElementById("l_title").innerText = t.l_title;
    document.getElementById("l_desc").innerText = t.l_desc;
}

function unlock() {
    document.getElementById("mainApp").style.opacity = "1";
    document.getElementById("mainApp").style.pointerEvents = "all";
    document.getElementById("accessSection").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        unlock();
    }

    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const user = prompt("ADMIN USER:");
        const pass = prompt("ADMIN PASS:");

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
        out.innerHTML = "<h4>🔍 Analyzing technical solutions...</h4>";
       
        const fd = new FormData(e.target);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        const res = await fetch(`/advisory`, { method: "POST", body: fd });
        const data = await res.json();
        const curLang = localStorage.getItem("user_lang") || "en";
       
        out.innerHTML = `
            <div id="finalReport" class="report-box">
                <h3 style="color:#01579b; border-bottom:2px solid #ffd600;">TACTICAL ACTION PLAN</h3>
                <p style="white-space: pre-wrap;">${data.data}</p>
                <hr>
                <p style="font-size:0.7em; color:gray;"><strong>Legal Notice:</strong> ${translations[curLang].l_desc}</p>
            </div>`;
        document.getElementById("actionBtns").style.display = "flex";

        // Iniciar cronómetro de privacidad
        document.getElementById("timerBox").style.display = "block";
        let timeLeft = 300;
        clearInterval(timer);
        timer = setInterval(() => {
            timeLeft--;
            document.getElementById("secs").innerText = timeLeft;
            if(timeLeft <= 0) location.reload();
        }, 1000);
    };
});

function downloadPDF() { html2pdf().from(document.getElementById("finalReport")).save("SmartCargo_Report.pdf"); }
function shareWA() { window.open(`https://wa.me/?text=${encodeURIComponent(document.getElementById("finalReport").innerText)}`, '_blank'); }
