# ==============================================================================
# SMARTCARGO-AIPA BACKEND - CONSTANTES FIJAS DE PRECIOS Y SERVICIOS
# Utilizado para el procesamiento de pagos con Stripe y blindaje de informes.
# ==============================================================================

# --- MENSAJE LEGAL ADICIONAL PARA INFORMES (Ajustado para importación) ---
# La importación en endpoints.py busca: PRICE_LEGAL_DISCLAIMER_TEXT
PRICE_LEGAL_DISCLAIMER_TEXT = (
    "SmartCargo ofrece asesoría informativa. No se responsabiliza por información falsa o incompleta subida por el usuario."
)

# --- NIVELES DE SERVICIO FIJOS (Por envío) ---
SERVICE_LEVELS = {
    "LEVEL_BASIC": {
        "name": "Revisión Esencial",
        "price_usd": 35.00,
        "description": "Validación AWB, embalaje básico, etiquetas obligatorias, certificación ISPM-15, PDF simple.",
        "features": ["AWB & Carga Real Validation", "Basic Packaging Analysis", "Mandatory Labels Check", "ISPM-15 Pallet Confirmation", "Simple Diagnostic PDF"]
    },
    "LEVEL_PROFESSIONAL": {
        "name": "Optimización Completa",
        "price_usd": 65.00,
        "description": "Todo Básico + Validación IA fotográfica, optimización de cajas, detección de riesgos DG informativa, PDF detallado.",
        "features": ["LEVEL_BASIC", "AI Photo Validation", "AWB/Photo Consistency Check", "Box/Pallet Optimization Suggestions", "Informational DG Risk Identification", "Detailed Ready-to-Ship PDF"]
    },
    "LEVEL_PREMIUM": {
        "name": "Asesoría Integral",
        "price_usd": 120.00, 
        "description": "Todo Profesional + Evaluación de temperatura, alertas DG avanzadas, sugerencias de materiales certificados, asesoría completa de documentos, Reporte PDF avanzado.",
        "features": ["LEVEL_PROFESSIONAL", "Temperature/Sensitive Goods Evaluation", "Advanced DG Alerting (Informational)", "Certified Alternative Material Suggestions", "Full AWB Document Checklist", "Advanced Comprehensive PDF Report"]
    }
}

# --- EXTRAS OPCIONALES FIJOS (Por envío) ---
OPTIONAL_ADDONS = {
    "DG_ADVANCED_REVIEW": {
        "name": "Revisión Avanzada DG (Informativa)",
        "price_usd": 25.00
    },
    "MULTIPLE_OPTIMIZATION": {
        "name": "Optimización Múltiple de Pallets/Cajas",
        "price_usd": 30.00 
    },
    "RISK_ALERTS": {
        "name": "Alertas Personalizadas de Carga de Riesgo",
        "price_usd": 15.00
    }
}
