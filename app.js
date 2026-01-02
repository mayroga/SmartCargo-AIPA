// --- CONFIGURACIÓN INICIAL ---
const API_PATH = ""; // Dejar vacío si el JS se sirve desde el mismo servidor que el Python

const translations = {
    en: { 
        act: "1. Service Activation", 
        sol: "2. Solution Center", 
        desc: "Choose inspection or text consultation.",
        loading: "🔍 Generating Action Plan...",
        error: "❌ Connection error with the server."
    },
    es: { 
        act: "1. Activación de Servicio", 
        sol: "2. Centro de Soluciones", 
        desc: "Elija inspección o consulta escrita.",
        loading: "🔍 Generando Plan de Acción...",
        error: "❌ Error de conexión con el servidor."
    },
    fr: { 
        act: "1. Activation du Service", 
        sol: "2. Centre de Solutions", 
        desc: "Choisissez inspection ou consultation écrite.",
        loading: "🔍 Génération du plan d'action...",
        error: "❌ Erreur de conexión avec le serveur."
    },
    pt: { 
        act: "1. Ativação do Serviço", 
        sol: "2. Centro de Soluções", 
        desc: "Escolha inspeção ou consulta escrita.",
        loading: "🔍 Gerando Plano de Ação...",
        error: "❌ Erro de conexão com o servidor."
    },
    zh: { 
        act: "1. 服务激活", 
        sol: "2. 解决方案中心", 
        desc: "选择检查或文字咨询。",
        loading: "🔍 正在生成行动 plan...",
        error: "❌ 与服务器连接 error。"
    }
};

// --- GESTIÓN DE IDIOMA ---
function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations.en;
    
    // Actualizar textos en el HTML
    document.getElementById("t_act").innerText = t.act;
    document.getElementById("t_sol").innerText = t.sol;
    document.getElementById("p_desc").innerText = t.desc;
}

// --- DESBLOQUEO DE INTERFAZ ---
function unlock() {
    document.getElementById("mainApp").style.opacity = "1";
    document.getElementById("mainApp").style.pointerEvents = "all";
    document.getElementById("accessSection").style.display = "none";
}

// --- INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", () => {
    // Cargar idioma guardado
    const savedLang = localStorage.getItem("user_lang") || "en";
    setLang(savedLang);

    // Verificar si viene de un pago exitoso (Stripe Redirect)
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        unlock();
    }

    // Lógica del Botón Activar (Stripe o Admin)
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        
        // Intento de acceso administrativo
        const user = prompt("ADMIN USER (Leave blank for Stripe):");
        const pass = user ? prompt("ADMIN PASS:") : null;

        const fd = new FormData();
        fd.append("awb", awb); 
        fd.append("amount", amt);
        if(user) fd.append("user", user); 
        if(pass) fd.append("password", pass);

        try {
            const res = await fetch(`${API_PATH}/create-payment`, { method: "POST", body: fd });
            const data = await res.json();
            if(data.url) {
                window.location.href = data.url;
            } else {
                alert("Error: Access denied or invalid data.");
            }
        } catch (err) {
            alert("Server connection error.");
        }
    };

    // Manejo del Formulario de Asesoría (Gemini)
    const form = document.getElementById("advForm");
    form.onsubmit = async (e) => {
        e.preventDefault();
        const lang = localStorage.getItem("user_lang") || "en";
        const out = document.getElementById("advResponse");
        
        out.innerHTML = `<h4>${translations[lang].loading}</h4>`;
        document.getElementById("actionBtns").style.display = "none";

        const fd = new FormData(form);
        fd.append("lang", lang);

        try {
            const res = await fetch(`${API_PATH}/advisory`, { 
                method: "POST", 
                body: fd 
            });
            const data = await res.json();

            // Renderizar el reporte técnico
            out.innerHTML = `
                <div id="finalReport" class="report-box">
                    <h2 style="color:#01579b; border-bottom: 2px solid #01579b;">SMARTCARGO TECHNICAL REPORT</h2>
                    <div style="white-space: pre-wrap; font-family: sans-serif; line-height: 1.6;">
                        ${data.data}
                    </div>
                </div>`;
            
            document.getElementById("actionBtns").style.display = "flex";
        } catch (err) {
            out.innerHTML = `<p style="color:red;">${translations[lang].error}</p>`;
        }
    };
});

// --- SELECTOR DE ACCIÓN ---
function chooseAction(action) {
    document.getElementById("actionChoice").style.display = "none";
    document.getElementById("advForm").style.display = "block";
    document.getElementById("actionField").value = action;

    // Elementos de la interfaz
    const promptArea = document.getElementById("promptArea");
    const fileLabel = document.getElementById("fileLabel");
    const fileInput = document.getElementById("fileInput");

    if (action === "inspection") {
        // En inspección, queremos fotos y una breve descripción
        promptArea.style.display = "block";
        promptArea.placeholder = "Briefly describe the cargo or the specific problem you see...";
        fileLabel.style.display = "block";
        fileInput.style.display = "block";
    } else if (action === "consulta") {
        // En consulta, solo texto
        promptArea.style.display = "block";
        promptArea.placeholder = "Write your question here (regulations, routes, packaging, etc.)...";
        fileLabel.style.display = "none";
        fileInput.style.display = "none";
    } else if (action === "guide") {
        alert("Guidance: We recommend uploading photos if you have physical cargo issues, or writing a text query for logistics documents.");
        // Reiniciar para que elija una opción real
        document.getElementById("actionChoice").style.display = "flex";
        document.getElementById("advForm").style.display = "none";
    }
}

// --- UTILIDADES ---
function downloadPDF() { 
    const element = document.getElementById("finalReport");
    const opt = {
        margin:       1,
        filename:     'SmartCargo_Technical_Report.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
}

function shareWA() { 
    const text = document.getElementById("finalReport").innerText;
    const url = `https://wa.me/?text=${encodeURIComponent("*SMARTCARGO REPORT*\n\n" + text)}`;
    window.open(url, '_blank'); 
}
