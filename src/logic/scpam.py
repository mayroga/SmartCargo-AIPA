# src/logic/scpam.py
"""
SC-PAM core logic (Revisión Visual Documental, Análisis Papel-Foto,
Predicción de Riesgo Operacional, Pre-Simulación de Rechazo, RTC).
Estas funciones son deliberadamente conservadoras y explicativas:
- No clasifican DG oficialmente
- Solo ofrecen advertencias y recomendaciones (asesoría)
"""

from typing import Dict, Any
from requirements.standards.validation_codes import DG_KEYWORDS, INCOMPATIBLE_RISKS

def run_rvd(shipment) -> Dict[str, Any]:
    """
    Revisión Visual Documental: Verifica campos esenciales en el objeto Shipment
    (Packing List, Invoice, SLI simulados como presencia de datos críticos).
    """
    issues = []
    # Chequeos simples: nombres, peso, dimensiones, commodity
    if not shipment.shipper_name:
        issues.append("Falta nombre del shipper")
    if not shipment.consignee_name:
        issues.append("Falta nombre del consignee")
    if not shipment.weight_real_kg or shipment.weight_real_kg <= 0:
        issues.append("Peso real ausente o inválido")
    if not shipment.length_cm or not shipment.width_cm or not shipment.height_cm:
        issues.append("Dimensiones incompletas")
    if not shipment.commodity_type:
        issues.append("Descripción de mercancía ausente")
    return {"issues": issues, "status": "OK" if not issues else "ISSUES_FOUND"}

def run_acpf(shipment) -> Dict[str, Any]:
    """
    Análisis de consistencia Papel vs Foto (simulado aquí).
    Se basa en campos del shipment y metadatos (dg_risk_keywords).
    """
    inconsistencies = []
    # Ejemplo de regla: si dg_risk_keywords indica ALTO y is_dg=False -> inconsistencia
    if getattr(shipment, 'dg_risk_keywords', None) in ("ALTO", "HIGH") and not shipment.is_dg:
        inconsistencies.append("Posible DG detectado por IA pero no marcado como DG en documentos")
    return {"inconsistencies": inconsistencies, "status": "OK" if not inconsistencies else "INCONSISTENT"}

def run_pro(shipment) -> Dict[str, Any]:
    """
    Predicción de riesgo operacional: usa heurísticas simples para devolver índice.
    """
    score = 0
    reasons = []
    # Pallet madera sin ISPM
    if getattr(shipment, 'is_wood_pallet', False) and not getattr(shipment, 'ispm15_conf', False):
        score += 5
        reasons.append("Pallet de madera sin ISPM-15 confirmado")
    # Peso 0 o dimensiones 0
    if not shipment.weight_real_kg or shipment.weight_real_kg <= 0:
        score += 3
        reasons.append("Peso inválido o ausente")
    # DG keywords
    if getattr(shipment, 'dg_risk_keywords', None) in ("ALTO", "HIGH"):
        score += 4
        reasons.append("IA detectó riesgo DG en fotos/descripcion")
    # Resultado
    risk = "LOW"
    if score >= 7:
        risk = "HIGH"
    elif score >= 3:
        risk = "MEDIUM"
    return {"risk_score": score, "risk_level": risk, "reasons": reasons}

def run_psra(shipment) -> Dict[str, Any]:
    """
    Pre-Simulación de Rechazo: compara contra causas comunes y devuelve probabilidad.
    """
    reasons = []
    probability = 0.0
    # Regla: missing docs => alta probabilidad
    rvd = run_rvd(shipment)
    if rvd['status'] != "OK":
        probability += 0.5
        reasons.extend(rvd['issues'])
    pro = run_pro(shipment)
    if pro['risk_level'] == "HIGH":
        probability += 0.4
        reasons.extend(pro['reasons'])
    probability = min(probability, 0.99)
    verdict = "ACCEPT" if probability < 0.3 else ("REVIEW" if probability < 0.7 else "HIGH_RISK")
    return {"probability": probability, "verdict": verdict, "reasons": reasons}

def generate_rtc_report(shipment, rtc_payload) -> Dict[str, Any]:
    """
    Genera la estructura JSON del Ready-To-Counter report (no es PDF).
    """
    rtc = {
        "shipment_id": str(shipment.shipment_id),
        "summary": {
            "rvd": rtc_payload.get("rvd"),
            "acpf": rtc_payload.get("acpf"),
            "pro": rtc_payload.get("pro"),
            "psra": rtc_payload.get("psra"),
        },
        "recommendations": []
    }
    # Construir recomendaciones basadas en resultados
    if rtc_payload.get("rvd", {}).get("issues"):
        rtc["recommendations"].append("Completar campos faltantes en Packing List/Invoice/SLI.")
    if rtc_payload.get("pro", {}).get("risk_level") == "HIGH":
        rtc["recommendations"].append("Revisar embalaje, ISPM-15 y posible clasificación DG con su forwarder.")
    if rtc_payload.get("psra", {}).get("verdict") == "HIGH_RISK":
        rtc["recommendations"].append("No entregar al handler hasta corregir las observaciones.")
    return rtc
