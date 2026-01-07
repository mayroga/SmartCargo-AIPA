let imgB64 = ["","",""]; // 3 fotos
let role = "";
let timeLeft = 0;

const i18n = {
en:{legal:"PRIVATE ADVISORY. NOT IATA, NOT TSA, NOT DOT. NOT GOVERNMENT.",capture:"📷 UPLOAD PHOTO",get:"GET SOLUTION",master:"MASTER ACCESS",clear:"CLEAR CONSULT",prompt:"Describe your case...",analyzing:"Analyzing cargo data...",timer:"TIME:"},
es:{legal:"ASESORÍA PRIVADA. NO SOMOS IATA, TSA, DOT. NO GOBIERNO.",capture:"📷 SUBIR FOTO",get:"OBTENER SOLUCIÓN",master:"ACCESO MAESTRO",clear:"LIMPIAR CONSULTA",prompt:"Describa su caso...",analyzing:"Analizando datos de carga...",timer:"TIEMPO:"}
};

function changeLang(l){
document.getElementById('txt-legal').innerText=i18n[l].legal;
for(let i=1;i<=3;i++){ document.getElementById('txt-capture'+i).innerText=i18n[l].capture; }
document.getElementById('prompt').placeholder=i18n[l].prompt;
const tDiv=document.getElementById('timer'); if(tDiv.style.display==="block"){ let current=tDiv.innerText.split(" ")[1]; tDiv.innerText=`${i18n[l].timer} ${current}`; }
}

const params=new URLSearchParams(window.location.search);
if(params.get('access')==='granted'){
document.getElementById('accessSection').style.display='none';
document.getElementById('mainApp').style.display='block';
const t={"5":300,"15":900,"35":1800,"95":3600,"0":86400};
timeLeft=t[params.get('monto')]||300;
const tDiv=document.getElementById('timer'); tDiv.style.display="block";
setInterval(()=>{ if(timeLeft<=0){ alert("Session Expired"); location.href="/"; } let m=Math.floor(timeLeft/60); let s=timeLeft%60; let lang=document.getElementById('userLang').value; tDiv.innerText=`${i18n[lang].timer} ${m}:${s<10?'0':''}${s}`; timeLeft--; },1000);
}

function scRead(e,n){ const r=new FileReader(); r.onload=()=>{ imgB64[n-1]=r.result; document.getElementById('v'+n).src=r.result; document.getElementById('v'+n).style.display="block"; document.getElementById('txt-capture'+n).style.display="none"; }; r.readAsDataURL(e.target.files[0]); }

function activarVoz(){ const Speech=window.SpeechRecognition||window.webkitSpeechRecognition; if(!Speech) return alert("Voz no soportada"); const rec=new Speech(); rec.lang=document.getElementById('userLang').value==='es'?'es-ES':'en-US'; rec.start(); rec.onresult=(e)=>{ document.getElementById('prompt').value=e.results[0][0].transcript; }; }

async function pay(amt){ const fd=new FormData(); fd.append("amount",amt); fd.append("awb",document.getElementById('awb').value||"REF"); fd.append("user",document.getElementById('u').value); fd.append("password",document.getElementById('p').value); const r=await fetch('/create-payment',{method:'POST',body:fd}); const d=await r.json(); if(d.url) window.location.href=d.url; else alert("Access Denied"); }

async function run(){
if(!role) return alert("Please select your Role");
const out=document.getElementById('res'); const lang=document.getElementById('userLang').value;
out.style.display="block"; out.innerText=i18n[lang].analyzing;
const fd=new FormData(); fd.append("prompt", `Role: ${role}. Case: ${document.getElementById('prompt').value||""}`);
fd.append("lang",lang);
for(let i=0;i<3;i++){ if(imgB64[i]) fd.append("image_data",imgB64[i]); }
try{ const r=await fetch('/advisory',{method:'POST',body:fd}); const d=await r.json(); out.innerText=d.data||"SYSTEM: Error in response"; }catch(e){ console.error(e); out.innerText="Connection Error"; }
}

function limpiar(){ imgB64=["","",""]; for(let i=1;i<=3;i++){ document.getElementById('v'+i).style.display="none"; document.getElementById('txt-capture'+i).style.display="block"; } document.getElementById('prompt').value=""; document.getElementById('res').innerText=""; document.getElementById('res').style.display="none"; }

function selRole(r,el){ role=r; document.querySelectorAll('.role-btn').forEach(b=>b.classList.remove('selected')); el.classList.add('selected'); }

function ws(){ const text=document.getElementById('res').innerText; window.open("https://wa.me/?text="+encodeURIComponent(text)); }

function copy(){ const text=document.getElementById('res').innerText; navigator.clipboard.writeText(text); alert("Copied to clipboard"); }
