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

// Prompts técnicos del Auditor
const rolePrompts = {
    shipper: "Analiza esta carga como Inspector de Calidad. 1. Describe detalladamente el estado del embalaje (palet, film, cajas). 2. Identifica cualquier golpe o deformidad que pueda generar un reclamo del cliente. 3. Confirma si la mercancía proyecta una imagen de seguridad profesional. Sé crítico.",
    forwarder: "Actúa como Auditor de Forwarder. 1. Evalúa la estiba: ¿hay cajas aplastadas o mal apiladas? 2. Verifica visibilidad de etiquetas de manejo (Frágil, Flechas). 3. Determina si falta documentación pegada que pueda causar un 'Hold' en aduanas. Da una lista de correcciones necesarias.",
    trucker: "Evalúa riesgos de transporte terrestre. 1. ¿Está la carga balanceada? 2. Identifica riesgos de desplazamiento en curvas o frenados. 3. ¿Ves daños que te hagan sospechar que te culparán en el destino? ¿Te la regresarán? Sé muy específico con los riesgos físicos.",
    counter: "Inspección de alta velocidad para ingreso. 1. Busca inmediatamente: agujeros, manchas de humedad o precintos rotos. 2. ¿Son legibles los códigos de barras/etiquetas? 3. Clasifica el riesgo: Bajo (Aceptar), Medio (Inspección extra), Alto (Rechazo inmediato)."
};

let timer;

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations.en;
    document.getElementById("t_act").innerText = t.act;
    document.getElementById("t_sol").innerText = t.sol;
}

function unlock() {
    document.getElementById("mainApp").style.opacity = "1";
    document.getElementById("mainApp").style.pointerEvents = "all";
    document.getElementById("accessSection").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    // Manejo de Roles
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('roleInput').value = btn.dataset.role;
        };
    });

    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        unlock();
    }

    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const user = prompt("ADMIN USER (Opcional):");
        const pass = prompt("ADMIN PASS (Opcional):");

        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(user) fd.append("user", user); if(pass) fd.append("password", pass);

        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const loader = document.getElementById("loader");
        const out = document.getElementById("advResponse");
        const submitBtn = document.getElementById("submitBtn");
        
        loader.style.display = "block";
        submitBtn.disabled = true;
        out.innerHTML = "";
        
        const role = document.getElementById('roleInput').value;
        const userPrompt = document.getElementById('promptArea').value;
        
        // Construimos el prompt final combinando la instrucción de rol + el texto del usuario
        const finalPrompt = `ROL: ${role.toUpperCase()}. INSTRUCCIÓN TÉCNICA: ${rolePrompts[role]}. CLIENTE DICE: ${userPrompt}`;

        const fd = new FormData(e.target);
        fd.set("prompt", finalPrompt); // Reemplazamos el prompt simple por el técnico
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            const curLang = localStorage.getItem("user_lang") || "en";
            
            out.innerHTML = `
                <div id="finalReport" class="report-box">
                    <h3 style="color:#01579b; border-bottom:2px solid #ffd600; margin-top:0;">TACTICAL ACTION PLAN - SMARTCARGO</h3>
                    <p style="white-space: pre-wrap; font-size: 0.95em;">${data.data}</p>
                    <hr>
                    <p style="font-size:0.7em; color:gray;"><strong>Legal Notice:</strong> ${translations[curLang].l_desc}</p>
                </div>`;
            document.getElementById("actionBtns").style.display = "flex";

            // Timer de Privacidad
            document.getElementById("timerBox").style.display = "block";
            let timeLeft = 300;
            clearInterval(timer);
            timer = setInterval(() => {
                timeLeft--;
                document.getElementById("secs").innerText = timeLeft;
                if(timeLeft <= 0) location.reload();
            }, 1000);
        } catch (err) {
            out.innerHTML = "<p style='color:red;'>Error al conectar con el servidor.</p>";
        } finally {
            loader.style.display = "none";
            submitBtn.disabled = false;
        }
    };
});

function downloadPDF() { html2pdf().from(document.getElementById("finalReport")).save("SmartCargo_Technical_Report.pdf"); }
function shareWA() { window.open(`https://wa.me/?text=${encodeURIComponent(document.getElementById("finalReport").innerText)}`, '_blank'); }
