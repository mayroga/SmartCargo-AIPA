let lastLang = "en";
let role = "auto";

function changeLang(v){
    lastLang = v;
}

function selRole(r,el){
    role = r;
    document.querySelectorAll(".role").forEach(b=>b.classList.remove("selected"));
    el.classList.add("selected");
}

async function pay(amount){
    const fd = new FormData();
    fd.append("amount", amount);
    fd.append("awb", document.getElementById("awb").value || "GENERAL");
    fd.append("user", document.getElementById("u").value);
    fd.append("password", document.getElementById("p").value);

    const r = await fetch("/create-payment",{method:"POST",body:fd});
    const j = await r.json();
    if(j.url) location.href = j.url;
}

async function run(){
    const txt = document.getElementById("prompt").value;
    if(!txt) return;

    const fd = new FormData();
    fd.append("prompt", txt);
    fd.append("lang", lastLang);
    fd.append("role", role);

    const r = await fetch("/advisory",{method:"POST",body:fd});
    const j = await r.json();

    document.getElementById("res").style.display="block";
    document.getElementById("res").innerText = j.data;
}

window.onload = ()=>{
    const p = new URLSearchParams(window.location.search);
    if(p.get("access")==="granted"){
        document.getElementById("main").style.display="block";
    }
};
