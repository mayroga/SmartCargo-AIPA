const texts = {
    es: {
        h_subtitle: "Consultoría Técnica Independiente en Logística",
        l_aviso: "AVISO LEGAL DE BLINDAJE:",
        l_desc: "SMARTCARGO ADVISORY LLC es una firma de consultoría privada. NO somos una agencia del gobierno, NO somos TSA, IATA, DOT ni IMO...",
        b_title: "¿Por qué usar nuestro Asesor?",
        p_title: "Activar Servicio",
        app_title: "Centro de Soluciones Globales"
    },
    en: {
        h_subtitle: "Independent Technical Logistics Consulting",
        l_aviso: "LEGAL SHIELD NOTICE:",
        l_desc: "SMARTCARGO ADVISORY LLC is a private consulting firm. We are NOT a government agency, NOT TSA, IATA, DOT, or IMO...",
        b_title: "Why use our Advisor?",
        p_title: "Activate Service",
        app_title: "Global Solution Center"
    },
    pt: {
        h_subtitle: "Consultoria Técnica Independente em Logística",
        l_aviso: "AVISO DE PROTEÇÃO LEGAL:",
        l_desc: "SMARTCARGO ADVISORY LLC é uma empresa de consultoria privada. NÃO somos uma agência governamental, NÃO somos TSA, IATA, DOT ou IMO...",
        b_title: "Por que usar nosso Consultor?",
        p_title: "Ativar Serviço",
        app_title: "Centro de Soluções Globais"
    }
};

function changeLang(lang) {
    localStorage.setItem("lang", lang);
    const t = texts[lang];
    for (let id in t) {
        const el = document.getElementById(id);
        if (el) el.innerText = t[id];
    }
}

// Inactividad y Desbloqueo
let timer;
function resetTimer() {
    clearTimeout(timer);
    timer = setTimeout(() => {
        alert("Sesión cerrada por seguridad.");
        localStorage.clear();
        location.reload();
    }, 300000); // 5 min
}

function unlock() {
    document.getElementById("mainApp").style.display = "block";
    document.getElementById("accessSection").style.display = "none";
    resetTimer();
}

document.addEventListener("DOMContentLoaded", () => {
    changeLang(localStorage.getItem("lang") || "es");
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        unlock();
    }

    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const res = await fetch("/create-payment", {
            method: "POST",
            body: new URLSearchParams({ 'awb': awb, 'amount': amt })
        });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };
});
