const translations = {
    en: { act: "1. Activate Advisory", sol: "2. Solution Center" },
    es: { act: "1. Activar Asesoría", sol: "2. Centro de Soluciones" }
};

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    
    // Verificar si ya pagó
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        document.getElementById("mainApp").style.display = "block";
        document.getElementById("accessSection").style.display = "none";
    }

    // Botón de pago
    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const user = prompt("ADMIN USER (Optional):");
        const pass = user ? prompt("ADMIN PASS:") : "";

        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(user) fd.append("user", user); if(pass) fd.append("password", pass);

        const res = await fetch(`/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    // Formulario de Asesoría
    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<p>⏳ Analyzing cargo safety...</p>";
        
        const fd = new FormData(e.target);
        fd.append("lang", "es"); // Cambiar a "en" según necesidad

        try {
            const res = await fetch(`/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            out.innerHTML = `<div id="report" class="response-box">
                <strong style="color:#01579b">SMARTCARGO REPORT:</strong><br>
                <p style="white-space: pre-wrap;">${data.data}</p>
            </div>`;
            document.getElementById("actionBtns").style.display = "flex";
        } catch (err) {
            out.innerHTML = "Error connecting to server.";
        }
    };
});

function downloadPDF() { html2pdf().from(document.getElementById("report")).save("SmartCargo_ActionPlan.pdf"); }
function shareWA() { 
    const txt = document.getElementById("report").innerText;
    window.open(`https://wa.me/?text=${encodeURIComponent(txt)}`, '_blank'); 
}
