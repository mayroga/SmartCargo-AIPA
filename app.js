const dictionary = {
    en: {
        head: "SmartCargo ADVISORY",
        mT: "Why SmartCargo?",
        mD: "At **MAY ROGA LLC**, we provide stability to global trade. This system prevents cargo rejections, TSA/IATA fines, and damages, ensuring every participant contributes to a safe transport.",
        lT: "⚠️ Mandatory Legal Shield",
        lD: "Virtual preventive advisor. MAY ROGA LLC is NOT a gov entity, does NOT certify DG, and does NOT replace TSA/IATA inspections. This is expert technical advice.",
        btnP: "PAY & ACTIVATE",
        btnS: "GENERATE TECHNICAL REPORT"
    },
    es: {
        head: "Asesoría SmartCargo",
        mT: "¿Por qué SmartCargo?",
        mD: "En **MAY ROGA LLC**, aportamos estabilidad al comercio global. Este sistema previene rechazos de carga, multas de TSA/IATA y daños, asegurando que todos contribuyan a un transporte seguro.",
        lT: "⚠️ Blindaje Legal Obligatorio",
        lD: "Asesor preventivo virtual. MAY ROGA LLC NO es entidad gubernamental, NO certifica carga peligrosa y NO reemplaza inspecciones oficiales. Es asesoría técnica experta.",
        btnP: "PAGAR Y ACTIVAR",
        btnS: "GENERAR INFORME TÉCNICO"
    }
};

function setLang(l) {
    localStorage.setItem("lang", l);
    const t = dictionary[l] || dictionary.en;
    document.getElementById("h-title").innerText = t.head;
    document.getElementById("m-title").innerText = t.mT;
    document.getElementById("m-desc").innerHTML = t.mD;
    document.getElementById("l-title").innerText = t.lT;
    document.getElementById("l-desc").innerText = t.lD;
    document.getElementById("btn-pay").innerText = t.btnP;
    document.getElementById("btn-submit").innerText = t.btnS;
}

async function adminLogin() {
    const fd = new FormData();
    fd.append("user", document.getElementById("user").value);
    fd.append("password", document.getElementById("pass").value);
    const res = await fetch("/login-admin", { method: "POST", body: fd });
    if(res.ok) {
        document.getElementById("appSection").style.display = "block";
        document.getElementById("authSection").style.display = "none";
    } else { alert("Error"); }
}

async function pay() {
    const p = document.getElementById("priceSelect").value;
    const l = localStorage.getItem("lang") || "en";
    const res = await fetch("/create-payment", { method: "POST", headers: {"Content-Type": "application/x-www-form-urlencoded"}, body: `price=${p}&lang=${l}` });
    const data = await res.json();
    if(data.url) window.location.href = data.url;
}

document.getElementById("cargoForm").onsubmit = async (e) => {
    e.preventDefault();
    const out = document.getElementById("result");
    out.innerHTML = "<h4>🔍 Analizando bajo normativas internacionales...</h4>";
    const fd = new FormData(e.target);
    fd.append("prompt", document.getElementById("prompt").value);
    fd.append("lang", localStorage.getItem("lang") || "en");
    const files = document.getElementById("pics").files;
    for(let i=0; i<Math.min(files.length, 3); i++) fd.append("images", files[i]);

    const res = await fetch("/advisory", { method: "POST", body: fd });
    const data = await res.json();
    const cur = localStorage.getItem("lang") || "en";
    
    out.innerHTML = `<div class="report-frame">
        <h2 style="color:#002855; border-bottom:3px solid #ffd600;">TECHNICAL REPORT | MAY ROGA LLC</h2>
        <p style="white-space: pre-wrap;">${data.data}</p>
        <div style="font-size:0.7em; margin-top:30px; border-top:1px solid #000; padding-top:10px; color:#555;">
            <strong>LEGAL DISCLAIMER:</strong> ${dictionary[cur].lD}
        </div>
    </div><button onclick="window.print()">DESCARGAR REPORTE PDF</button>`;
};

window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('status') === 'success') {
        document.getElementById("appSection").style.display = "block";
        document.getElementById("authSection").style.display = "none";
    }
    setLang(localStorage.getItem("lang") || "en");
};
