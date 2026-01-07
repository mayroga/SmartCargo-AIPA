let imgB64 = "";
let lastLang = "en";
let selectedRole = "";

const ads = [
  "No holds. No fines.",
  "Prevent cargo delays.",
  "Avoid cargo returns.",
  "Protect your money.",
  "Cargo arrives compliant."
];

let i = 0;
setInterval(()=>{
  const el = document.getElementById("ad");
  if(el) el.innerText = ads[i++ % ads.length];
},3000);

function selRole(role, el){
  selectedRole = role;
  document.querySelectorAll(".role-btn").forEach(b=>b.classList.remove("selected"));
  el.classList.add("selected");
}

function loadPhoto(el){
  if(!el.files[0]) return;
  const r = new FileReader();
  r.onload = e=>{
    imgB64 = e.target.result;
    document.getElementById("img").src = imgB64;
  };
  r.readAsDataURL(el.files[0]);
}

async function pay(amount){
  const fd = new FormData();
  fd.append("amount", amount);
  fd.append("awb", document.getElementById("awb").value || "REF");
  fd.append("user", document.getElementById("adminUser").value);
  fd.append("password", document.getElementById("adminPass").value);
  const r = await fetch("/create-payment",{method:"POST",body:fd});
  const d = await r.json();
  if(d.url) location.href = d.url;
  else alert("Access denied");
}

async function analyze(){
  if(!selectedRole) return alert("Select role first");
  const fd = new FormData();
  fd.append("prompt", `ROLE: ${selectedRole}. ${document.getElementById("prompt").value}`);
  fd.append("image_data", imgB64);
  fd.append("lang", document.getElementById("langSwitch").value);

  document.getElementById("advResponse").innerText = "Analyzing cargo...";
  const r = await fetch("/advisory",{method:"POST",body:fd});
  const d = await r.json();
  document.getElementById("advResponse").innerText = d.data;
  lastLang = d.lang || "en";
}

async function translate(){
  const fd = new FormData();
  fd.append("text", document.getElementById("advResponse").innerText);
  fd.append("target", lastLang === "en" ? "es" : "en");
  const r = await fetch("/translate",{method:"POST",body:fd});
  const d = await r.json();
  document.getElementById("advResponse").innerText = d.text;
  lastLang = d.lang;
}

function sendWS(){
  window.open("https://wa.me/?text="+encodeURIComponent(document.getElementById("advResponse").innerText));
}

function copyText(){
  navigator.clipboard.writeText(document.getElementById("advResponse").innerText);
  alert("Copied to clipboard");
}

function clearAll(){
  if(!confirm("Clear image and analysis?")) return;
  imgB64 = "";
  selectedRole = "";
  document.getElementById("img").src = "";
  document.getElementById("prompt").value = "";
  document.getElementById("advResponse").innerText = "";
  document.querySelectorAll(".role-btn").forEach(b=>b.classList.remove("selected"));
}
