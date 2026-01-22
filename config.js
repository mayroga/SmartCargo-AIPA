// ==============================================================================
// SMARTCARGO ADVISORY - CONFIGURACIÓN DE CONOCIMIENTO Y TRADUCCIONES
// ==============================================================================

const CONFIG = {
    // Blindaje Legal y Textos de Interfaz
    labels: {
        en: {
            shield: "LEGAL SHIELD: WE ARE PRIVATE ADVISORS. NOT IATA/TSA/DOT. WE PROVIDE TECHNICAL SOLUTIONS; WE DON'T CERTIFY DG OR HANDLE CARGO.",
            solutionBtn: "Get Technical Solution",
            evidencePlaceholder: "Describe findings...",
            validateBtn: "Validate & Access"
        },
        es: {
            shield: "PROTECCIÓN LEGAL: SOMOS ASESORES PRIVADOS. NO SOMOS IATA/TSA/DOT. PROVEEMOS SOLUCIONES TÉCNICAS; NO CERTIFICAMOS DG NI MANIPULAMOS CARGA.",
            solutionBtn: "Obtener Solución Técnica",
            evidencePlaceholder: "Describa los hallazgos...",
            validateBtn: "Validar y Acceder"
        }
    },

    // Estructura de Precios y Roles (Exacto a la Foto)
    tiers: {
        "C5": { name: "Courier", price: 5 },
        "S15": { name: "Standard", price: 15 },
        "C35": { name: "Critical", price: 35 },
        "P95": { name: "Project", price: 95 }
    },

    // Estándares Técnicos de Referencia para el "Cerebro"
    standards: {
        units: "Always provide measurements in both [Inches] INC and [Centimeters] CM.",
        max_height: {
            passenger: "63 INC / 160 CM",
            freighter: "96 INC / 243 CM",
            triple_seven: "118 INC / 300 CM"
        },
        wood_packaging: "ISPM-15 International Standard is mandatory for all wooden pallets.",
        dg_warning: "Informative alert: Segregation must be checked per IATA DGR Table 9.3.A."
    },

    // Respuestas de Error Comunes
    errors: {
        no_role: "Please select a Role and Service Tier.",
        no_awb: "AWB/Reference is required for tracking and logging.",
        missing_data: "Insufficient data to provide a technical solution."
    }
};

// Exponer la configuración globalmente
window.smartCargoConfig = CONFIG;
