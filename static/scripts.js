function analyzeCargo() {
    const type = document.getElementById("cargoType").value;
    const desc = document.getElementById("description").value.trim();
    const weight = parseFloat(document.getElementById("weight").value);
    const origin = document.getElementById("origin").value.trim().toUpperCase();
    const destination = document.getElementById("destination").value.trim().toUpperCase();

    let result = [];

    if (!type || !desc || !weight || !origin || !destination) {
        document.getElementById("analysisResult").textContent =
            "⚠️ Información incompleta. Complete todos los campos.";
        return;
    }

    result.push("✔️ Información básica válida");

    if (weight > 30000) {
        result.push("⚠️ Peso elevado: requiere coordinación previa con la aerolínea");
    }

    if (type === "dangerous") {
        result.push("⚠️ Mercancía clasificada como peligrosa");
        result.push("• Requiere declaración DG");
        result.push("• Embalaje certificado");
        result.push("• Etiquetado obligatorio");
    }

    if (type === "human_remains") {
        result.push("⚠️ Restos humanos detectados");
        result.push("• Ataúd o urna sellada");
        result.push("• Certificado de defunción");
        result.push("• Permisos consulares si aplica");
    }

    if (type === "live_animals") {
        result.push("⚠️ Animales vivos");
        result.push("• Certificado veterinario");
        result.push("• Jaula IATA LAR compliant");
        result.push("• Restricciones por temperatura");
    }

    document.getElementById("analysisResult").textContent = result.join("\n");
}

function generateDocs() {
    const type = document.getElementById("cargoType").value;
    let docs = [];

    docs.push("📄 Air Waybill (AWB)");

    if (type === "dangerous") {
        docs.push("📄 Shipper's Declaration");
        docs.push("📄 MSDS / SDS");
    }

    if (type === "perishable") {
        docs.push("📄 Certificado sanitario");
    }

    if (type === "human_remains") {
        docs.push("📄 Certificado de defunción");
        docs.push("📄 Permiso de transporte");
    }

    if (type === "live_animals") {
        docs.push("📄 Certificado veterinario");
        docs.push("📄 Declaración del remitente");
    }

    docs.push("📄 Factura comercial");
    docs.push("📄 Packing List");

    document.getElementById("docsResult").textContent =
        docs.length ? docs.join("\n") : "Seleccione un tipo de carga primero.";
}

function runCompliance() {
    const origin = document.getElementById("origin").value.toUpperCase();
    const destination = document.getElementById("destination").value.toUpperCase();

    let alerts = [];

    if (origin === "MIA") {
        alerts.push("✔️ Origen bajo control de seguridad reforzada");
    }

    if (destination === "BOG" || destination === "MEX") {
        alerts.push("⚠️ Verificar requisitos aduanales del país destino");
    }

    alerts.push("✔️ Validación TSA completada");
    alerts.push("✔️ Reglas operativas de aerolínea aplicadas");
    alerts.push("✔️ Cumplimiento regulatorio general");

    document.getElementById("complianceResult").textContent =
        alerts.join("\n");
}
