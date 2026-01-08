let imgB64 = ["","",""];
let role = "";
let cargoInfo = { type:"", state:"", special:"" };

const i18n = {
    en:{legal:"PRIVATE ADVISORY. NOT IATA, NOT TSA, NOT DOT. NOT GOVERNMENT.",capture:"📷 UPLOAD PHOTO",get:"GET SOLUTION",master:"MASTER ACCESS",clear:"CLEAR CONSULT",prompt:"Describe your case...",analyzing:"Analyzing cargo data...",timer:"TIME:",askType:"What type of cargo is it?",askState:"Is it solid, liquid or gas?",askSpecial:"Any special characteristic: flammable, corrosive, fragile?" },
    es:{legal:"ASESORÍA PRIVADA. NO SOMOS IATA, TSA, DOT. NO GOBIERNO.",capture:"📷 SUBIR FOTO",get:"OBTENER SOLUCIÓN",master:"ACCESO MAESTRO",clear:"LIMPIAR CONSULTA",prompt:"Describa su caso...",analyzing:"Analizando datos de carga...",timer:"TIEMPO:",askType:"¿Qué tipo de mercancía?",askState:"¿Es sólido, líquido o gas?",askSpecial:"¿Alguna característica especial: inflamable, corrosivo, frágil?" }
};

// DETECTOR DE ACCESO (NUEVO)
window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('access') === 'granted') {
        document.getElementById('accessSection').style.display = "none";
        document.getElementById('mainApp').style.display = "block";
        const awb = params.get('awb') || "REF-OK";
        const tDiv = document.getElementById('timer');
        tDiv.style.display = "block";
        tDiv.innerText = "ACCESS GRANTED | AWB: " + decodeURIComponent(awb);
    }
});

function changeLang(l){
    document.getElementById('txt-legal').innerText=i18n[l].legal;
    for(let i=1;i<=3;i++) document.getElementById('txt-capture'+i).innerText=i18n[l].capture;
    document.getElementById('prompt').placeholder=i18n[l].prompt;
}

function scRead(e,n){
    const r=new FileReader();
    r.onload=()=>{ imgB64[n-1]=r.result; document.getElementById('v'+n).src=r.result; document.getElementById('v'+n).style.display="block"; document.getElementById('txt-capture'+n).style.display="none"; };
    r.readAsDataURL(e.target.files[0]);
}

function activarVoz(){
    const Speech=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!Speech) return alert("Voz no soportada");
    const rec=new Speech();
    rec.lang=document.getElementById('userLang').value==='es'?'es-ES':'en-US';
    rec.start();
    rec.onresult=(e)=>{ document.getElementById('prompt').value=e.results[0][0].transcript; };
}

function escuchar(){
    const text=document.getElementById('res').innerText;
    if(!text) return;
    const utter=new SpeechSynthesisUtterance(text);
    utter.lang=document.getElementById('userLang').value==='es'?'es-ES':'en-US';
    window.speechSynthesis.speak(utter);
}

function limpiar(){
    imgB64=["","",""];
    for(let i=1;i<=3;i++){
        document.getElementById('v'+i).style.display="none";
        document.getElementById('txt-capture'+i).style.display="block";
    }
    document.getElementById('prompt').value="";
    document.getElementById('res').innerText="";
    document.getElementById('res').style.display="none";
    cargoInfo={type:"", state:"", special:""};
}

function selRole(r,el){ role=r; document.querySelectorAll('.role-btn').forEach(b=>b.classList.remove('selected')); el.classList.add('selected'); }

async function preRun(){
    const lang=document.getElementById('userLang').value;
    if(!cargoInfo.type){ cargoInfo.type=prompt(i18n[lang].askType); if(!cargoInfo.type) return; }
    if(!cargoInfo.state){ cargoInfo.state=prompt(i18n[lang].askState); if(!cargoInfo.state) return; }
    if(!cargoInfo.special){ cargoInfo.special=prompt(i18n[lang].askSpecial); if(!cargoInfo.special) cargoInfo.special="none"; }
    run();
}

async function run(){
    if(!role) return alert("Please select your Role");
    const out=document.getElementById('res'); 
    const lang=document.getElementById('userLang').value;
    out.style.display="block"; 
    out.innerText=i18n[lang].analyzing;

    const fd=new FormData(); 
    let promptText=`Role: ${role}. Cargo info: Type: ${cargoInfo.type}, State: ${cargoInfo.state}, Special: ${cargoInfo.special}. Additional: ${document.getElementById('prompt').value||""}`;
    fd.append("prompt", promptText);
    fd.append("lang",lang);
    for(let i=0;i<3;i++){ if(imgB64[i]) fd.append("image_data",imgB64[i]); }

    try{
        const r=await fetch('/advisory',{method:'POST',body:fd});
        const d=await r.json();
        out.innerText=d.data||"SYSTEM: Error in response";
    }catch(e){ console.error(e); out.innerText="Connection Error"; }
}

function ws(){ const text=document.getElementById('res').innerText; window.open("https://wa.me/?text="+encodeURIComponent(text)); }
function copy(){ const text=document.getElementById('res').innerText; navigator.clipboard.writeText(text); alert("Copied to clipboard"); }

async function pay(amt){ 
    const fd=new FormData(); 
    fd.append("amount",amt); 
    fd.append("awb",document.getElementById('awb').value||"REF"); 
    fd.append("user",document.getElementById('u').value); 
    fd.append("password",document.getElementById('p').value); 
    const r=await fetch('/create-payment',{method:'POST',body:fd}); 
    const d=await r.json(); 
    if(d.url) window.location.href=d.url; 
    else alert("Access Denied"); 
}
