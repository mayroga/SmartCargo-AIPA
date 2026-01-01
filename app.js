const translations = {
    en: {
        h_subtitle: "Technical Consulting by MAY ROGA LLC",
        l_aviso: "LEGAL SHIELD NOTICE:",
        l_desc: "MAY ROGA LLC is a private consulting firm. We are NOT a government agency, NOT TSA, IATA, DOT, or IMO. We do not hold DG licenses nor handle cargo physically. Our role is to provide technical advice to prevent errors. By using this system, you accept our solutions as preventive suggestions.",
        b_title: "Why use our Advisor?",
        p_title: "Activate Professional Service",
        app_title: "Global Solution Center",
        b_html: `<div class="benefit-card">✅ <strong>Avoid Holds:</strong> Don't let your cargo stop at any global hub.</div><div class="benefit-card">✅ <strong>Save Money:</strong> Prevent costly storage and rejections.</div>`
    },
    es: {
        h_subtitle: "Consultoría Técnica por MAY ROGA LLC",
        l_aviso: "AVISO LEGAL DE BLINDAJE:",
        l_desc: "MAY ROGA LLC es una firma de consultoría privada. NO somos una agencia del gobierno, NO somos TSA, IATA, DOT ni IMO. NO poseemos licencia de DG ni manejamos carga físicamente. Nuestra función es asesorar técnicamente para evitar errores de estiba y documentación. Al usar este sistema, usted acepta que nuestras soluciones son sugerencias de cumplimiento preventivo.",
        b_title: "¿Por qué usar nuestro Asesor?",
        p_title: "Activar Servicio Profesional",
        app_title: "Centro de Soluciones Globales",
        b_html: `<div class="benefit-card">✅ <strong>Evite Retrasos:</strong> No deje que su carga se detenga en ningún puerto.</div><div class="benefit-card">✅ <strong>Ahorre Dinero:</strong> Prevenga gastos de almacenamiento y rechazos.</div>`
    },
    pt: {
        h_subtitle: "Consultoria Técnica por MAY ROGA LLC",
        l_aviso: "AVISO DE PROTEÇÃO LEGAL:",
        l_desc: "MAY ROGA LLC é uma empresa de consultoria privada. NÃO somos uma agência governamental...",
        b_title: "Por que usar nosso consultor?",
        p_title: "Ativar Serviço",
        app_title: "Centro de Soluções",
        b_html: `<div class="benefit-card">✅ Evite Atrasos</div><div class="benefit-card">✅ Economize Dinheiro</div>`
    },
    zh: {
        h_subtitle: "MAY ROGA LLC 的技术咨询",
        l_aviso: "法律保护公告:",
        l_desc: "MAY ROGA LLC 是一家私人咨询公司。我们不是政府机构...",
        b_title: "为什么选择我们的咨询？",
        p_title: "激活服务",
        app_title: "全球解决方案中心",
        b_html: `<div class="benefit-card">✅ 避免停滞</div><div class="benefit-card">✅ 节省资金</div>`
    },
    fr: {
        h_subtitle: "Conseil Technique par MAY ROGA LLC",
        l_aviso: "AVIS DE PROTECTION JURIDIQUE:",
        l_desc: "MAY ROGA LLC est un cabinet de conseil privé...",
        b_title: "Pourquoi utiliser notre conseil ?",
        p_title: "Activer le service",
        app_title: "Centre de solutions",
        b_html: `<div class="benefit-card">✅ Éviter les retards</div><div class="benefit-card">✅ Économiser de l'argent</div>`
    },
    hi: {
        h_subtitle: "MAY ROGA LLC द्वारा तकनीकी परामर्श",
        l_aviso: "कानूनी सुरक्षा नोटिस:",
        l_desc: "MAY ROGA LLC एक निजी परामर्श फर्म है। हम सरकारी एजेंसी नहीं हैं...",
        b_title: "हमारी सलाह का उपयोग क्यों करें?",
        p_title: "सेवा सक्रिय करें",
        app_title: "समाधान केंद्र",
        b_html: `<div class="benefit-card">✅ देरी से बचें</div><div class="benefit-card">✅ पैसे बचाएं</div>`
    }
};

function changeLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations['en'];
    
    document.getElementById("h_subtitle").innerText = t.h_subtitle;
    document.getElementById("l_aviso").innerText = t.l_aviso;
    document.getElementById("l_desc").innerText = t.l_desc;
    document.getElementById("b_title").innerText = t.b_title;
    document.getElementById("b_list").innerHTML = t.b_html;
    document.getElementById("p_title").innerText = t.p_title;
    document.getElementById("app_title").innerText = t.app_title;
}

document.addEventListener("DOMContentLoaded", () => {
    // INGLÉS POR DEFECTO
    const savedLang = localStorage.getItem("user_lang") || "en";
    changeLang(savedLang);
    
    // Lógica de pago y desbloqueo... (Mantenida de versiones anteriores)
});

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
            <h3 style="color:#002855;">TECHNICAL REPORT | MAY ROGA LLC</h3>
            <p style="white-space: pre-wrap;">${data.data}</p>
            <div class="legal-footer">
                <strong>SHIELD NOTICE:</strong> ${translations[lang].l_desc}
            </div>
        </div>
        <button onclick="window.print()" style="width:100%; margin-top:10px;">Print / Save PDF</button>
    `;
    e.target.reset(); // BORRA FOTOS Y TEXTO AUTOMÁTICAMENTE
};
