const translations = {
    en: {
        act: "1. Service Activation",
        sol: "2. Solution Center",
        t_photo: "TAP TO TAKE PHOTOS",
        l_desc: "PRIVATE ADVISORS. Not IATA/TSA/DOT. We provide technical solutions.",
        btn_cam: "OPEN CAMERA"
    },
    es: {
        act: "1. Activación",
        sol: "2. Centro de Soluciones",
        t_photo: "TOCA PARA TOMAR FOTOS",
        l_desc: "ASESORES PRIVADOS. No IATA/TSA/DOT. Soluciones técnicas.",
        btn_cam: "ABRIR CÁMARA"
    }
};

const rolePrompts = {
    shipper: "Auditor de Calidad: Revisa integridad de cajas, paletizado y estética profesional.",
    forwarder: "Auditor FWD: Revisa etiquetas, estiba para vuelo y posibles causas de retención.",
    trucker: "Chofer: Revisa balance de peso, seguridad de trincado y daños para no ser culpado.",
    counter: "Counter: Revisa humedad, roturas inmediatas y legibilidad de guía."
};

let timer;

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = translations[lang];
    document.getElementById("t_act").innerText = t.act;
    document.getElementById("t_sol").innerText = t.sol;
    document.getElementById("t_photo").innerText = t.t_photo;
    document.querySelector(".btn-camera").innerText = t.btn_cam;

    document.getElementById("btnEn").classList.toggle("lang-active", lang === 'en');
    document.getElementById("btnEs").classList.toggle("lang-active", lang === 'es');
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "en");

    // Lógica de Selección de Roles
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('roleInput').value = this.dataset.role;
        });
    });

    // Contador de fotos seleccionadas
    document.getElementById('fileInput').addEventListener('change', function() {
        const count = this.files.length;
        document.getElementById('fileCount').innerText = count > 0 ? `✅ ${count} photos ready` : "";
    });

    // Verificación de Acceso
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        document.getElementById("mainApp").style.opacity = "1";
        document.getElementById("mainApp").style.pointerEvents = "all";
        document.getElementById("accessSection").style.display = "none";
    }

    // Botón de Pago
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        
        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    // Envío del Formulario
    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const loader = document.getElementById("loader");
        const out = document.getElementById("advResponse");
        const submitBtn = document.getElementById("submitBtn");
        
        loader.style.display = "block";
        submitBtn.disabled = true;
        out.innerHTML = "";
        
        const fd = new FormData(e.target);
        const role = document.getElementById('roleInput').value;
        const userText = document.getElementById('promptArea').value;
        
        fd.set("prompt", `ROLE: ${role}. CONTEXT: ${rolePrompts[role]}. USER NOTE: ${userText}`);
        fd.append("lang", localStorage.getItem("user_lang") || "en");

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            
            out.innerHTML = `
                <div id="finalReport" class="report-box">
                    <h5 style="color:#01579b; margin-top:0;">📋 AUDIT REPORT</h5>
                    <p style="white-space: pre-wrap; font-size: 0.95em;">${data.data}</p>
                    <hr>
                    <small style="color:gray;">May Roga LLC - Private Advisory</small>
                </div>`;
            document.getElementById("actionBtns").style.display = "flex";
        } catch (err) {
            out.innerHTML = "Connection Error.";
        } finally {
            loader.style.display = "none";
            submitBtn.disabled = false;
        }
    };
});

function downloadPDF() { html2pdf().from(document.getElementById("finalReport")).save("SmartCargo_Audit.pdf"); }
function shareWA() { 
    const text = document.getElementById("finalReport").innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`); 
}
