const API_PATH = "";

function unlock() {
    document.getElementById("mainApp").style.opacity = "1";
    document.getElementById("mainApp").style.pointerEvents = "all";
    document.getElementById("accessSection").style.display = "none";
    document.getElementById("benefits").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("access") === "granted" || localStorage.getItem("sc_auth") === "true") {
        localStorage.setItem("sc_auth", "true");
        unlock();
    }

    document.getElementById("activateBtn").onclick = async () => {
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const user = prompt("ADMIN USER:");
        const pass = prompt("ADMIN PASSWORD:");

        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(user) fd.append("user", user); if(pass) fd.append("password", pass);

        const res = await fetch(`${API_PATH}/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML = "<h4>🔍 Verificando normativas federales y estatales...</h4>";
        
        const fd = new FormData(e.target);
        fd.append("lang", "es");

        const res = await fetch(`${API_PATH}/advisory`, { method: "POST", body: fd });
        const data = await res.json();
        
        let reportClass = data.data.includes("🔴") ? "alert-red" : "alert-green";
        
        out.innerHTML = `
            <div id="finalReport" class="${reportClass}">
                <h3 style="margin-top:0;">CERTIFICACIÓN TÉCNICA SMARTCARGO</h3>
                <p style="white-space: pre-wrap;">${data.data}</p>
                <hr>
                <p style="font-size:0.7em;"><em>SmartCargo Advisory LLC es una firma de consultoría independiente. Este reporte busca facilitar el cumplimiento normativo.</em></p>
            </div>
            <button onclick="window.print()" style="margin-top:10px; width:100%;">Imprimir Reporte para el Operador</button>
        `;
    };
});
