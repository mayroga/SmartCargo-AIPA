const API_PATH = "";
let timeoutHandle;

function startTimer() {
    clearTimeout(timeoutHandle);
    document.getElementById("timerBox").style.display = "block";
    timeoutHandle = setTimeout(() => {
        alert("Sesión cerrada por seguridad. Todos los datos temporales han sido eliminados.");
        localStorage.clear();
        location.href = "/";
    }, 300000); // 5 minutos
}

function unlock() {
    document.getElementById("mainApp").style.opacity = "1";
    document.getElementById("mainApp").style.pointerEvents = "all";
    document.getElementById("accessSection").style.display = "none";
    startTimer();
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
        const pass = prompt("ADMIN PASS:");

        const fd = new FormData();
        fd.append("awb", awb); fd.append("amount", amt);
        if(user) fd.append("user", user); if(pass) fd.append("password", pass);

        const res = await fetch(`${API_PATH}/create-payment`, { method: "POST", body: fd });
        const data = await res.json();
        if(data.url) window.location.href = data.url;
    };

    document.getElementById("advForm").onsubmit = async (e) => {
        e.preventDefault();
        startTimer(); // Reinicia el tiempo al trabajar
        const out = document.getElementById("advResponse");
        out.innerHTML = "<h4>🔍 Procesando cumplimiento legal...</h4>";
        
        const fd = new FormData(e.target);
        fd.append("lang", "es");

        try {
            const res = await fetch(`${API_PATH}/advisory`, { method: "POST", body: fd });
            const data = await res.json();
            
            let reportClass = data.data.includes("🔴") ? "alert-red" : "alert-green";
            
            out.innerHTML = `
                <div id="finalReport" class="${reportClass}">
                    <h3 style="margin-top:0;">REPORTE PROFESIONAL SMARTCARGO</h3>
                    <p style="white-space: pre-wrap;">${data.data}</p>
                    <p style="font-size:0.7em; border-top:1px solid #ccc; padding-top:10px;">
                        ⚠️ PRIVACIDAD: Este reporte es efímero. Imprímalo ahora si lo necesita.
                    </p>
                </div>
                <button onclick="window.print()" style="width:100%;">Imprimir / Guardar PDF</button>
            `;
            e.target.reset(); // Borra fotos y texto inmediatamente del formulario
        } catch (err) {
            out.innerHTML = "<p>Error técnico. Intente de nuevo.</p>";
        }
    };
});

// Reinicia el contador ante cualquier actividad
document.onmousemove = startTimer;
document.onkeypress = startTimer;
