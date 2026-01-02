const API_PATH = "";

const translations = {
    en:{ act:"1. Service Activation", sol:"2. Solution Center", desc:"Upload photos first. Text is optional." },
    es:{ act:"1. Activación de Servicio", sol:"2. Centro de Soluciones", desc:"Suba fotos primero. El texto es opcional." },
    fr:{ act:"1. Activation du Service", sol:"2. Centre de Solutions", desc:"Téléchargez les photos d'abord. Texte optionnel." },
    pt:{ act:"1. Ativação do Serviço", sol:"2. Centro de Soluções", desc:"Envie fotos primeiro. Texto opcional." },
    zh:{ act:"1. 服务激活", sol:"2. 解决方案中心", desc:"先上传照片，文字可选。" }
};

function setLang(lang){
    localStorage.setItem("user_lang", lang);
    const t = translations[lang] || translations.en;
    document.getElementById("t_act").innerText = t.act;
    document.getElementById("t_sol").innerText = t.sol;
    document.getElementById("p_desc").innerText = t.desc;
}

function unlock(){
    document.getElementById("mainApp").style.opacity="1";
    document.getElementById("mainApp").style.pointerEvents="all";
    document.getElementById("accessSection").style.display="none";
}

document.addEventListener("DOMContentLoaded", ()=>{
    setLang(localStorage.getItem("user_lang") || "en");

    const params = new URLSearchParams(window.location.search);
    if(params.get("access")==="granted" || localStorage.getItem("sc_auth")==="true"){
        localStorage.setItem("sc_auth","true");
        unlock();
    }

    document.getElementById("activateBtn").onclick = async ()=>{
        const awb = document.getElementById("awbField").value || "N/A";
        const amt = document.getElementById("priceSelect").value;
        const user = prompt("ADMIN USER:");
        const pass = prompt("ADMIN PASS:");

        const fd = new FormData();
        fd.append("awb",awb);
        fd.append("amount",amt);
        if(user) fd.append("user",user);
        if(pass) fd.append("password",pass);

        const res = await fetch(`${API_PATH}/create-payment`,{method:"POST",body:fd});
        const data = await res.json();
        if(data.url) window.location.href=data.url;
    };

    document.getElementById("advForm").onsubmit = async (e)=>{
        e.preventDefault();
        const out = document.getElementById("advResponse");
        out.innerHTML="<h4>🔍 Inspecting images and generating action plan...</h4>";

        const fd = new FormData(e.target);
        fd.append("lang",localStorage.getItem("user_lang")||"en");

        const res = await fetch(`${API_PATH}/advisory`,{method:"POST",body:fd});
        const data = await res.json();

        out.innerHTML = `
            <div id="finalReport" class="report-box">
                <h3>TECHNICAL ACTION PLAN</h3>
                ${data.data}
            </div>
        `;
        document.getElementById("actionBtns").style.display="flex";
    };
});

function downloadPDF(){
    html2pdf().from(document.getElementById("finalReport"))
        .save("SmartCargo_Report.pdf");
}

function shareWA(){
    window.open(
        `https://wa.me/?text=${encodeURIComponent(document.getElementById("finalReport").innerText)}`,
        "_blank"
    );
}
