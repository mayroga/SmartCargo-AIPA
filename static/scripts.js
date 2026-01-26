let lang = "EN";

document.getElementById("langBtn").onclick = () => {
  lang = lang === "EN" ? "ES" : "EN";
  document.getElementById("langBtn").innerText = lang;
};

async function validateCargo() {
  const payload = {
    mawb: mawb.value,
    hawb: hawb.value,
    origin: origin.value,
    destination: destination.value,
    weight: Number(weight.value),
    height: Number(height.value),
    role: role.value
  };

  const res = await fetch("/validate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  let text = `
  <h2>${data.semaforo}</h2>
  <p>${data.advisory}</p>
  <small>${data.legal}</small>
  `;

  if (lang === "ES") {
    text = text.replace("NOT ACCEPTABLE", "NO ACEPTABLE")
               .replace("ACCEPTABLE", "ACEPTABLE");
  }

  document.getElementById("results").innerHTML = text;
}
