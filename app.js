const translations = {
    en: { 
        act: "1. Service Activation", 
        sol: "2. Tactical Solution Center", 
        m_title: "Practical Solutions",
        m_desc: "We solve errors in the logistics chain. Immediate action plans for shippers, drivers, and operators.",
        l_desc: "PRIVATE ADVISORY: Technical suggestions to avoid financial loss. Not a legal body."
    },
    es: { 
        act: "1. Activación de Servicio", 
        sol: "2. Centro de Soluciones Tácticas", 
        m_title: "Soluciones Prácticas",
        m_desc: "Corregimos errores en toda la cadena logística. Planes de acción inmediata para transportistas y agentes.",
        l_desc: "ASESORÍA PRIVADA: Sugerencias técnicas para evitar pérdidas. No somos un organismo legal."
    }
};

let countdown;

function startPrivacyTimer() {
    let timeLeft = 300; // 5 minutos
    document.getElementById("timerDisplay").style.display = "block";
    clearInterval(countdown);
    countdown = setInterval(() => {
        timeLeft--;
        document.getElementById("secs").innerText = timeLeft;
        if(timeLeft <= 0) {
            clearInterval(countdown);
            location.reload(); // Limpieza total por privacidad
        }
    }, 1000);
}

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations.en;
    document.querySelectorAll("[id]").forEach(el => {
        if(t[el.id.replace('t_','').replace('m_','').replace('l_','')]) {
            el.innerText = t[el.id.replace('t_','').replace('m_','').replace('l_','')];
        }
    });
}

document.getElementById("advForm").onsubmit = async (e) => {
    e.preventDefault();
    const out = document.getElementById("advResponse");
    out.innerHTML = "<h4>🚀 Generating your Tactical Action Plan...</h4>";
    
    const fd = new FormData(e.target);
    fd.append("lang", localStorage.getItem("user_lang") || "en");

    try {
        const res = await fetch(`/advisory`, { method: "POST", body: fd });
        const data = await res.json();
        
        out.innerHTML = `
            <div id="finalReport" class="report-box">
                <h3 style="color:#01579b; border-bottom:2px solid #ffd600;">📋 TACTICAL ACTION PLAN</h3>
                <p style="white-space: pre-wrap; font-family: monospace;">${data.data}</p>
                <hr>
                <p style="font-size:0.7em; color:gray;"><strong>Expert Note:</strong> This is a private suggestion to optimize flow and prevent holds.</p>
            </div>`;
        
        document.getElementById("actionBtns").style.display = "flex";
        startPrivacyTimer(); // Inicia la autodestrucción de info por privacidad
    } catch (err) {
        out.innerHTML = "Error connecting to advisor. Check your connection.";
    }
};

// ... Funciones de unlock, payment y PDF se mantienen igual ...
