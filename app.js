const dictionary = {
    en: { 
        head: "SmartCargo ADVISORY", 
        legal: "⚠️ Legal Notice", 
        desc: "Virtual preventive advisor for air and maritime cargo (Does NOT certify, Does NOT inspect, Does NOT replace regulators). Developed to protect the customer's merchandise through analysis, predictions, and 100% automatic alerts. MAY ROGA LLC is a private firm.", 
        price: "Select service to activate:",
        btnA: "ACTIVATE NOW",
        btnS: "GET ANALYSIS"
    },
    es: { 
        head: "Asesoría SmartCargo", 
        legal: "⚠️ Aviso Legal", 
        desc: "Asesor preventivo virtual para la carga aérea y marítima (NO certifica, NO inspecciona, NO reemplaza reguladores). Desarrollado para proteger la mercancía del cliente mediante análisis, predicciones y alertas 100% automáticas. MAY ROGA LLC es una firma privada.", 
        price: "Seleccione servicio para activar:",
        btnA: "ACTIVAR AHORA",
        btnS: "OBTENER ANÁLISIS"
    },
    zh: { head: "SmartCargo 技术中心", legal: "⚠️ 法律声明", desc: "货运虚拟预防顾问（不提供认证，不进行检查，不取代监管机构）。MAY ROGA LLC 是一家私人咨询公司。", price: "选择要激活的服务：", btnA: "立即激活", btnS: "获取分析" },
    hi: { head: "SmartCargo तकनीकी केंद्र", legal: "⚠️ कानूनी नोटिस", desc: "कार्गो के लिए आभासी निवारक सलाहकार (प्रमाणित नहीं करता, निरीक्षण नहीं करता)। MAY ROGA LLC एक निजी परामर्श फर्म है।", price: "सक्रिय करने के लिए सेवा चुनें:", btnA: "अभी सक्रिय करें", btnS: "विश्लेषण प्राप्त करें" }
};

function setLang(lang) {
    localStorage.setItem("lang", lang);
    const t = dictionary[lang] || dictionary.en;
    document.getElementById("h-title").innerText = t.head;
    document.getElementById("l-title").innerText = t.legal;
    document.getElementById("l-desc").innerText = t.desc;
    document.getElementById("p-text").innerText = t.price;
    document.getElementById("btn-activate").innerText = t.btnA;
    document.getElementById("btn-submit").innerText = t.btnS;
}

function activate() {
    document.getElementById("appSection").style.display = "block";
    document.getElementById("authSection").style.display = "none";
}

document.getElementById("cargoForm").onsubmit = async (e) => {
    e.preventDefault();
    const out = document.getElementById("result");
    out.innerHTML = "<h4>🔍 Processing Technical Report...</h4>";
    
    const fd = new FormData();
    fd.append("prompt", document.getElementById("prompt").value);
    fd.append("lang", localStorage.getItem("lang") || "en");
    
    const files = document.getElementById("pics").files;
    for(let i=0; i<Math.min(files.length, 3); i++) { fd.append("images", files[i]); }

    try {
        const res = await fetch("/advisory", { method: "POST", body: fd });
        const data = await res.json();
        const currentLang = localStorage.getItem("lang") || "en";
        
        out.innerHTML = `
            <div class="report-out">
                <h3 style="color:#002855; border-bottom:2px solid #ffd600;">TECHNICAL REPORT | MAY ROGA LLC</h3>
                <p style="white-space: pre-wrap;">${data.data}</p>
                <div style="font-size:0.75em; margin-top:20px; border-top:1px solid #000; padding-top:10px;">
                    <strong>SHIELD NOTICE:</strong> ${dictionary[currentLang].desc}
                </div>
            </div>
            <button onclick="window.print()" style="width:100%; margin-top:10px;">Save as PDF</button>
        `;
        e.target.reset();
    } catch (err) {
        out.innerHTML = "Error processing request. Check your connection.";
    }
};

setLang(localStorage.getItem("lang") || "en");
setTimeout(() => { location.reload(); }, 300000); // Sesión de 5 min
