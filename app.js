// CONEXIÓN AL BACKEND
const API_PATH = "https://smartcargo-aipa.onrender.com"; 

function setLang(lang) {
    localStorage.setItem("user_lang", lang);
    const t = {
        en: { act: "1. Activation", sol: "2. Solution Center", p1: "Describe issue or upload 3 photos." },
        es: { act: "1. Activación", sol: "2. Centro de Soluciones", p1: "Describa el problema o suba 3 fotos." }
    };
    const sel = t[lang] || t['en'];
    document.getElementById("t_act").innerText = sel.act;
    document.getElementById("t_sol").innerText = sel.sol;
}

function unlockSystem() {
    const main = document.getElementById("mainApp");
    if (main) {
        main.style.opacity = "1";
        main.style.pointerEvents = "all";
        document.getElementById("accessSection").style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setLang(localStorage.getItem("user_lang") || "es");

    // DESBLOQUEO SI HAY ACCESO
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("smartcargo_auth") === "true") {
        localStorage.setItem("smartcargo_auth", "true");
        unlockSystem();
    }

    // ACTIVACIÓN POR ADMIN O PAGO
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const price = document.getElementById("servicePrice").value;
        const user = prompt("ADMIN USER:");
        const pass = prompt("ADMIN PASS:");

        const fd = new FormData();
        fd.append("awb", awb);
        fd.append("amount", price);
        if(user) fd.append("user", user);
        if(pass) fd.append("password", pass);

        try {
            const res = await fetch(`${API_PATH}/create-payment`, { method: "POST", body: fd });
            const data = await res.json();
            if(data.url) window.location.href = data.url; 
        } catch (err) {
            alert("Error: No se pudo conectar con SmartCargo-AIPA");
        }
    };

    // GENERAR SOLUCIONES
    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<h3>🔍 Generando múltiples soluciones técnicas...</h3>";
        
        const fd = new FormData(e.target);
        fd.append("lang", localStorage.getItem("user_lang") || "es");

        try {
            const res = await fetch(`${API_PATH}/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `<div id="finalReport">${data.data}</div>`;
            document.getElementById("actionBtns").style.display = "flex";
        } catch (err) {
            out.innerHTML = "<h3>⚠️ Error de comunicación con el Asesor Virtual.</h3>";
        }
    };
});
