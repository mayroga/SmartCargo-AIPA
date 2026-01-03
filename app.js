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

const rolePrompts = {
    shipper: "Analiza como Inspector de Calidad: 1. Describe embalaje (palet, film). 2. Identifica deformidades. 3. Evalúa profesionalismo visual.",
    forwarder: "Actúa como Auditor de Forwarder: 1. Evalúa estiba y aplastamiento. 2. Verifica etiquetas de manejo. 3. Identifica riesgos de 'Hold' aduanero.",
    trucker: "Evalúa riesgos de transporte: 1. Balance de carga. 2. Riesgos de desplazamiento. 3. Identifica daños pre-existentes para evitar reclamos injustos.",
    counter: "Inspección rápida: 1. Detecta agujeros o humedad. 2. Legibilidad de códigos. 3. Clasifica: Bajo, Medio o Alto Riesgo."
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
    // Inicializar idioma
    const userLang = localStorage.getItem("user_lang") || (navigator.language.startsWith('es') ? 'es' : 'en');
    setLang(userLang);

    // Manejo de Roles (Botones)
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('roleInput').value = btn.dataset.role;
        };
    });

    // Verificar si ya pagó
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        unlock();
    }

    // Lógica de Pago / Admin
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const user = prompt("ADMIN USER (Opcional):");
        const pass = prompt("ADMIN PASS (Opcional):");

        const fd = new FormData();
        fd.append("awb", awb);
        fd.append("amount", amt);
        if(user) fd.append("user", user);
        if(pass) fd.append("password", pass);

        try {
            const res = await fetch(`/create-payment`, { method: "POST", body: fd });
            const data = await res.json();
            if(data.url) window.location.href = data.url;
        } catch (e) { alert("Error connecting to Stripe"); }
    };

    // Envío de Auditoría Técnica
    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const loader = document.getElementById("loader");
        const out = document.getElementById("advResponse");
        const submitBtn = document.getElementById("submitBtn");
        
        loader.style.display = "block";
        submitBtn.disabled = true;
        out.innerHTML = "";
        
        const role = document.getElementById('roleInput').value;
        const userText = document.getElementById('promptArea').value;
        
        // Construcción del Prompt Maestro
        const finalPrompt = `[ROLE: ${role.toUpperCase()}] [GUIDE: ${rolePrompts[role]}] [USER_NOTE: ${userText}]`;

        const fd = new FormData(e.target);
        fd.set("prompt", finalPrompt); // Inyectamos el prompt técnico
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            const curLang = localStorage.getItem("user_lang") || "en";
            
            out.innerHTML = `
                <div id="finalReport" class="report-box">
                    <h4 style="color:#01579b; border-bottom:2px solid #ffd600; margin-top:0;">TACTICAL ACTION PLAN - SMARTCARGO</h4>
                    <p style="white-space: pre-wrap; font-size: 0.95em;">${data.data}</p>
                    <hr>
                    <p style="font-size:0.7em; color:gray;"><strong>Legal Notice:</strong> ${translations[curLang].l_desc}</p>
                </div>`;
            
            document.getElementById("actionBtns").style.display = "flex";

            // Timer de Seguridad (5 Minutos)
            document.getElementById("timerBox").style.display = "block";
            let timeLeft = 300;
            clearInterval(timer);
            timer = setInterval(() => {
                timeLeft--;
                document.getElementById("secs").innerText = timeLeft;
                if(timeLeft <= 0) {
                    localStorage.removeItem("sc_auth");
                    location.reload();
                }
            }, 1000);

        } catch (err) {
            out.innerHTML = "<p style='color:red;'>Server Error. Please check your connection.</p>";
        } finally {
            loader.style.display = "none";
            submitBtn.disabled = false;
        }
    };
});

// PDF y WhatsApp
function downloadPDF() { 
    const element = document.getElementById("finalReport");
    const opt = { margin: 1, filename: 'SmartCargo_Report.pdf', image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2 }, jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' } };
    html2pdf().set(opt).from(element).save();
}

function shareWA() { 
    const text = document.getElementById("finalReport").innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent("SmartCargo AI Report:\n\n" + text)}`, '_blank'); 
}
