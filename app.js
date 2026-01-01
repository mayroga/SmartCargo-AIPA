const translations = {
    en: {
        h_subtitle: "BY MAY ROGA LLC",
        l_aviso: "⚠️ Legal Notice",
        l_desc: "Virtual preventive advisor for cargo. NO certifies, NO inspects. MAY ROGA LLC provides data-based expert advice to prevent losses.",
        p_title: "ACTIVATE NOW",
        app_title: "Solution Center"
    },
    es: {
        h_subtitle: "POR MAY ROGA LLC",
        l_aviso: "⚠️ Aviso Legal",
        l_desc: "Asesor preventivo virtual. NO certifica, NO inspecciona. MAY ROGA LLC ofrece asesoría experta basada en datos para evitar pérdidas.",
        p_title: "ACTIVAR AHORA",
        app_title: "Centro de Soluciones"
    },
    zh: { h_subtitle: "由 MAY ROGA LLC 提供", l_aviso: "⚠️ 法律声明", l_desc: "货运虚拟预防顾问。不认证，不检查。MAY ROGA LLC 提供基于数据的专家建议以防止损失。", p_title: "现在激活", app_title: "解决方案中心" },
    hi: { h_subtitle: "MAY ROGA LLC द्वारा", l_aviso: "⚠️ कानूनी नोटिस", l_desc: "कार्गो के लिए आभासी निवारक सलाहकार। प्रमाणित नहीं करता, निरीक्षण नहीं करता। MAY ROGA LLC नुकसान को रोकने के लिए डेटा-आधारित विशेषज्ञ सलाह प्रदान करता है।", p_title: "अब सक्रिय करें", app_title: "समाधान केंद्र" },
    fr: { h_subtitle: "PAR MAY ROGA LLC", l_aviso: "⚠️ Avis Légal", l_desc: "Conseiller préventif virtuel. NE certifie PAS, N'inspecte PAS. MAY ROGA LLC fournit des conseils d'experts basés sur des données.", p_title: "ACTIVER", app_title: "Centre de Solutions" },
    pt: { h_subtitle: "POR MAY ROGA LLC", l_aviso: "⚠️ Aviso Legal", l_desc: "Consultor preventivo virtual. NÃO certifica, NÃO inspeciona. A MAY ROGA LLC oferece assessoria especializada.", p_title: "ATIVAR", app_title: "Centro de Soluções" }
};

function changeLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations['en'];
    document.getElementById("h_subtitle").innerText = t.h_subtitle;
    document.getElementById("l_aviso").innerText = t.l_aviso;
    document.getElementById("l_desc").innerHTML = translations[lang].l_desc || translations['en'].l_desc;
}

let timer;
function startInactivityTimer() {
    clearTimeout(timer);
    timer = setTimeout(() => {
        alert("Session expired for security.");
        location.reload();
    }, 300000); // 5 minutes
}

document.addEventListener("DOMContentLoaded", () => {
    changeLang(localStorage.getItem("user_lang") || "en");
    
    document.getElementById("activateBtn").onclick = () => {
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
        startInactivityTimer();
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        startInactivityTimer();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<h4>🔍 Analyzing...</h4>";
        
        const fd = new FormData(e.target);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch("/advisory", { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `
                <div class="report-box">
                    <h3>MAY ROGA LLC | Technical Report</h3>
                    <p style="white-space: pre-wrap;">${data.data}</p>
                    <div class="legal-footer">${translations[localStorage.getItem("user_lang") || "en"].l_desc}</div>
                </div>
                <button onclick="window.print()">Print PDF</button>
            `;
            e.target.reset(); // Privacidad: Borra fotos y texto al terminar
        } catch (err) {
            out.innerHTML = "<p>Error. Please try again.</p>";
        }
    };
});
