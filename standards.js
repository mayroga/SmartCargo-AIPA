// ==============================================================================
// SMARTCARGO-ADVISORY — CONSTANTES OFICIALES
// ==============================================================================

export const AWB_MANDATORY_FIELDS = [
    { key: "SHIPPER", description: "Dueño real de la mercancía (responsable legal)" },
    { key: "CONSIGNEE", description: "Destinatario final" },
    { key: "ADDRESS", description: "Dirección completa (no PO Boxes)" },
    { key: "INTERNATIONAL_PHONE", description: "Número telefónico internacional válido" },
    { key: "WEIGHT_REAL_VOLUMETRIC", description: "Peso real vs peso volumétrico" },
    { key: "DIMENSIONS_EXACT", description: "Dimensiones exactas" },
    { key: "COMMODITY_TYPE", description: "Tipo específico de mercancía" },
    { key: "AIRPORT_CODE", description: "Código IATA del aeropuerto" },
    { key: "PERMITTED_STATUS", description: "Si está permitido transportarlo" }
];

export const ISPM_15_STANDARD = {
    NORMA: "ISPM-15 (Norma Internacional de Medidas Fitosanitarias)",
    SELLOS_OBLIGATORIOS: [
        "HT - Heat Treated (tratamiento térmico)",
        "Fumigación certificada",
        "Timbre internacional visible"
    ]
};

export const MANDATORY_VALIDATION_POINTS = [
    "Etiquetas IATA",
    "Etiquetas de orientación",
    "Etiquetas de temperatura",
    "Documentación correcta",
    "Embalaje firme",
    "Cajas en buen estado",
    "No mezclar mercancías incompatibles",
    "No usar cinta negra",
    "Carga seca (sin humedad visible)",
    "Pallets certificados ISPM-15",
    "Sello de fumigación visible (si aplica)",
    "Declarar Dry Ice (si aplica)"
];

export const UNIVERSAL_LABELS = [
    "THIS SIDE UP",
    "FRAGILE",
    "PERISHABLE",
    "TEMPERATURE CONTROL",
    "DRY ICE",
    "LIVE ANIMALS",
    "BATTERIES",
    "CARGO AIRCRAFT ONLY",
    "ORIENTACIÓN",
    "ADVERTENCIA"
];

export const CORE_LEGAL_DISCLAIMER =
    "SmartCargo ofrece asesoría informativa. No es un servicio certificado IATA/TSA/FAA/DOT. No clasifica mercancía peligrosa. Para DG consulte un especialista certificado o la aerolínea.";

export const PRICE_LEGAL_DISCLAIMER =
    "SmartCargo no se responsabiliza por información falsa o incompleta proporcionada por el usuario.";

export const ELEGANT_SERVICE_TIERS = [
    {
        level: "Básico",
        name: "Revisión Esencial",
        price: "$35",
        features: [
            "Validación AWB y Carga Real",
            "Análisis Básico Peso/Volumen",
            "Verificación Etiquetas IATA",
            "Confirmación ISPM-15",
            "PDF simple con diagnóstico"
        ],
        perceived_value: "Refleja responsabilidad y prevención."
    },
    {
        level: "Profesional",
        name: "Optimización Completa",
        price: "$65",
        features: [
            "Todo el Básico",
            "Validación Fotográfica IA",
            "Detecta inconsistencias AWB/Fotos",
            "Sugerencias de optimización",
            "Detección informativa DG",
            "PDF avanzado para Courier"
        ],
        perceived_value: "Precio justo por protección y reducción de riesgos."
    },
    {
        level: "Premium",
        name: "Asesoría Integral",
        price: "$120",
        features: [
            "Todo Profesional",
            "Evaluación temperatura/sensibilidad",
            "Alertas DG y legales informativas",
            "Sugerencias materiales certificados",
            "Asesoría completa documentos",
            "Reporte PDF avanzado total"
        ],
        perceived_value: "Servicio VIP completo."
    }
];

export const OPTIONAL_ADDONS_DISPLAY = [
    { name: "Revisión DG Avanzada", price: "$25" },
    { name: "Optimización múltiple de pallets", price: "$30" },
    { name: "Alertas personalizadas de riesgo", price: "$15" }
];


// 🚨 DATABASE DE ALERTAS PARA LA CONSOLA OPERACIONAL (Sync con main.py)
window.standards = { 
    ALERTS_DB: {
        "R001": { msg: "Pallet de madera sin sello ISPM-15.", desc: "Alto riesgo fitosanitario/aduanero. La carga será DEVUELTA. Requiere pallet HT o cambio a plástico." },
        "R002": { msg: "Altura excede límite de ULD estándar (180cm).", desc: "Riesgo de rechazo por sobredimensión o límite de puerta de avión. Requiere re-paletizado inmediato." },
        "R003": { msg: "Embalaje CRÍTICO (Roto/Fuga).", desc: "Violación TSA/IATA. Rechazo inmediato en rampa. Requiere re-embalaje total y revisión del contenido." },
        "R004": { msg: "Etiquetas DG/Frágil/Orientación Faltantes.", desc: "Incumplimiento de placarding (TSA/IATA). Riesgo de clasificación errónea en bodega." },
        "R005": { msg: "Segregación DG CRÍTICA (Mezcla con NO DG).", desc: "Peligro de incompatibilidad química/incendio. Rechazo y posible multa. Separe inmediatamente." },
        "R006": { msg: "Discrepancia de Peso AWB/Físico.", desc: "Alto riesgo de HOLD, re-facturación y retraso. Verifique y corrija el AWB." },
        "R007": { msg: "Contenido DG requiere documento Shipper's Declaration.", desc: "Documento obligatorio DG faltante o inconsistente. Causa un HOLD inmediato." },
        "R008": { msg: "Altura excede límite de 213 cm (Screening TSA).", desc: "La carga excede el límite de 7 pies para inspección canina/ETD. Riesgo de deconstrucción y re-paletizado." },
        "R009": { msg: "Etiquetas DG/Frío no orientadas hacia afuera.", desc: "Riesgo de clasificación errónea por personal de muelle. Gire los bultos o reubique etiquetas para visibilidad total." }
    }
};
