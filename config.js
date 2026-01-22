// ==============================================================================
// SMARTCARGO ADVISORY - CONFIGURACIÓN INTEGRAL (IDIOMAS, ESTÁNDARES Y PRECIOS)
// ==============================================================================

const i18n = {
    en: {
        legal: "PRIVATE ENTITY - NOT IATA, TSA, DOT OR GOVERNMENT. <br> STRATEGIC ADVISORS PREVENTING ERRORS AND MAXIMIZING CAPITAL.",
        title: "SMARTCARGO ADVISORY",
        promo: "MITIGATING HOLDS AND RETURNS — THINKING FOR YOUR CARGO — 360° LOGISTICS SOLUTIONS — MAY ROGA LLC",
        exec: "EXECUTE ADVISORY",
        placeholder: "Describe the technical situation here...",
        roles: ["Trucker", "Forwarder", "Counter Staff", "Shipper/Owner"]
    },
    es: {
        legal: "ENTIDAD PRIVADA - NO SOMOS IATA, TSA, DOT NI GOBIERNO. <br> ASESORES ESTRATÉGICOS PREVINIENDO ERRORES Y MAXIMIZANDO CAPITAL.",
        title: "ASESORÍA SMARTCARGO",
        promo: "MITIGAMOS RETENCIONES Y RETORNOS — PENSAMOS POR TU CARGA — SOLUCIONES LOGÍSTICAS 360° — MAY ROGA LLC",
        exec: "EJECUTAR ASESORÍA",
        placeholder: "Describa la situación técnica aquí...",
        roles: ["Camionero", "Forwarder", "Agente Counter", "Dueño/Shipper"]
    }
};

const SMARTCARGO_STANDARDS = {
    AWB_FIELDS: [
        "SHIPPER (Legal responsibility)",
        "CONSIGNEE (Final destination)",
        "EXACT DIMENSIONS (INC/CM)",
        "REAL vs VOLUMETRIC WEIGHT",
        "ISPM-15 WOOD STAMP"
    ],
    CRITICAL_ALERTS: {
        "R001": "Pallet missing ISPM-15 stamp. High risk of return.",
        "R002": "Height exceeds 180cm. Possible ULD rejection.",
        "R003": "Damaged packaging. Immediate TSA/IATA violation.",
        "R005": "DG Segregation error. Risk of fire and heavy fines."
    }
};

const SERVICE_TIERS = [
    { name: "Essential", price: 35, features: ["AWB Validation", "Basic Volumetric Analysis"] },
    { name: "Professional", price: 65, features: ["AI Photo Validation", "DG Informative Detection"] },
    { name: "Premium", price: 120, features: ["Full Document Advisory", "Risk Mitigation Report"] }
];

const CORE_LEGAL_DISCLAIMER = "SmartCargo offers informative advisory. It is not an IATA/TSA/FAA/DOT certified service. It does not classify dangerous goods. Consult a certified specialist for regulated materials.";

// Exportar para uso en app.js
window.i18n = i18n;
window.standards = SMARTCARGO_STANDARDS;
window.tiers = SERVICE_TIERS;
