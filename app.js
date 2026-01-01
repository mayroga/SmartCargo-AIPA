const translations = {
    en: {
        h_subtitle: "Independent Technical Logistics Consulting",
        l_aviso: "LEGAL SHIELD NOTICE:",
        l_desc: "SMARTCARGO ADVISORY LLC is a private consulting firm. We are NOT a government agency (TSA, IATA, DOT, IMO). We do not hold DG licenses nor handle cargo physically. Advice provided consists of suggestions for preventive compliance.",
        b_title: "Why Use Our Advisory?",
        b1: "✅ Avoid Holds: Ensure smooth movement in any global hub.",
        b2: "✅ Save Money: Prevent costly storage and rejections.",
        p_title: "Activate Professional Service",
        app_title: "Global Solution Center"
    },
    es: {
        h_subtitle: "Consultoría Técnica Independiente en Logística",
        l_aviso: "AVISO LEGAL DE BLINDAJE:",
        l_desc: "SMARTCARGO ADVISORY LLC es una firma de consultoría privada. NO somos una agencia del gobierno, NO somos TSA, IATA, DOT ni IMO. NO poseemos licencia de DG ni manejamos carga físicamente. Nuestra función es asesorar técnicamente para evitar errores de estiba y documentación. Al usar este sistema, usted acepta que nuestras soluciones son sugerencias de cumplimiento preventivo.",
        b_title: "¿Por qué usar nuestra asesoría?",
        b1: "✅ Evite Retrasos: Asegure fluidez en cualquier puerto.",
        b2: "✅ Ahorre Dinero: Prevenga gastos de almacenamiento.",
        p_title: "Activar Servicio Profesional",
        app_title: "Centro de Soluciones Globales"
    },
    // ... Agregar pt, zh, fr, hi siguiendo el mismo formato
};

function changeLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations['en'];
    document.getElementById("h_subtitle").innerText = t.h_subtitle;
    document.getElementById("l_aviso").innerText = t.l_aviso;
    document.getElementById("l_desc").innerText = t.l_desc;
    document.getElementById("b_title").innerText = t.b_title;
    document.getElementById("b1").innerText = t.b1;
    document.getElementById("b2").innerText = t.b2;
    document.getElementById("p_title").innerText = t.p_title;
    document.getElementById("app_title").innerText = t.app_title;
}

document.getElementById("advForm").onsubmit = async (e) => {
    e.preventDefault();
    const lang = localStorage.getItem("user_lang") || "en";
    const out = document.getElementById("advResponse");
    out.innerHTML = "<h4>🔍 Processing Compliance...</h4>";
    
    const fd = new FormData(e.target);
    fd.append("lang", lang);

    const res = await fetch("/advisory", { method: "POST", body: fd });
    const data = await res.json();
    
    out.innerHTML = `
        <div id="printArea">
            <h3 style="color:#002855;">TECHNICAL ADVISORY REPORT</h3>
            <p style="white-space: pre-wrap; font-size:1.1em;">${data.data}</p>
            <div class="legal-footer">
                <strong>${translations[lang].l_aviso}</strong><br>
                ${translations[lang].l_desc}
            </div>
        </div>
        <button onclick="window.print()" style="width:100%; margin-top:10px;">Print / Save PDF</button>
    `;
    e.target.reset();
};

document.addEventListener("DOMContentLoaded", () => {
    changeLang(localStorage.getItem("user_lang") || "en");
});
