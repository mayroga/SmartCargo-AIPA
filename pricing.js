// ==============================================================================
// SMARTCARGO-ADVISORY - PRECIOS, PLANES Y PERCEPCIÓN
// ==============================================================================

// --- NIVELES DE SERVICIO ---
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

// --- EXTRAS ---
export const OPTIONAL_ADDONS_DISPLAY = [
    { name: "Revisión DG Avanzada", price: "$25" },
    { name: "Optimización múltiple de pallets", price: "$30" },
    { name: "Alertas personalizadas de riesgo", price: "$15" }
];
