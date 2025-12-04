# src/requirements/legal/guardrails.py

# ============================================================================== 
# SMARTCARGO-AIPA BACKEND - REGLAS LEGALES INMUTABLES (SECCIÓN 3)
# ==============================================================================

PROHIBITED_ACTIONS_DG = [
    "Declarar oficialmente mercancía peligrosa (DG)",
    "Clasificar mercancía bajo UN number o Clase 1–9",
    "Emitir certificaciones DG",
    "Enseñar procedimientos avanzados que requieren certificación IATA",
    "Indicar 'este producto es DG Clase X'",
    "Aprobar baterías",
    "Dar entrenamientos técnicos DG",
    "Enseñar a llenar el Shipper’s Declaration",
    "Reemplazar a un especialista certificado"
]

PERMITTED_LEGAL_ADVICE = [
    "Asesorar de forma general y educativa (sin certificar)",
    "Advertir riesgos y sugerir que el artículo puede ser regulado",
    "Recomendar contactar a un especialista DG certificado",
    "Explicar documentos, procesos básicos y consideraciones generales",
    "Guiar sobre embalaje seguro NO DG",
    "Analizar fotos para detectar riesgos visuales",
    "Educar sobre normas para carga aceptada",
    "Orientar sin reemplazar a un experto"
]
