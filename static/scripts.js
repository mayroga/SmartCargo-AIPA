let lang="en";

function goStep2(){
page1.classList.add("hidden");
page2.classList.remove("hidden");
}

function restart(){
location.reload();
}

function validate(){
const data=new FormData();
["mawb","hawb","role","origin","destination","cargo_type","weight","length","width","height","dot"]
.forEach(id=>data.append(id,document.getElementById(id).value));

const photos=document.getElementById("photos").files;
for(let i=0;i<photos.length && i<3;i++) data.append("files",photos[i]);

fetch("/validate",{method:"POST",body:data})
.then(r=>r.json()).then(showResult);
}

function showResult(res){
page2.classList.add("hidden");
result.classList.remove("hidden");
semaforo.innerText=res.status==="GREEN"?"🟢 ACCEPTABLE":"🔴 NOT ACCEPTABLE";
analysis.innerText=res.advisor;
issues.innerText=res.issues?.join("\n")||"";

const preview=document.getElementById("photosPreview");
preview.innerHTML="";
const input=document.getElementById("photos");
[...input.files].forEach(f=>{
const img=document.createElement("img");
img.src=URL.createObjectURL(f);
img.className="thumb";
img.onclick=()=>openModal(img.src);
preview.appendChild(img);
});
}

function openModal(src){
modal.style.display="flex";
modalImg.src=src;
}
function closeModal(){modal.style.display="none"}

function sendWhatsApp(){
window.open(`https://wa.me/?text=${encodeURIComponent(analysis.innerText)}`);
}

function speakResult(){
speechSynthesis.speak(new SpeechSynthesisUtterance(analysis.innerText));
}

function toggleLang(){
lang=lang==="en"?"es":"en";
document.querySelector("h3").innerText=lang==="es"?"Registrar / Validar Carga":"Register / Validate Cargo";
}
