from typing import List
from models import Carga, Documento, ResultadoValidacion
from datetime import datetime

# ----------------------
# REGLAS OBLIGATORIAS POR TIPO DE CARGA
# ----------------------
REQUIRED_DOCS = {
    "GEN": ["invoice", "packingList", "sli", "awbDoc"],
    "DG": ["invoice", "packingList", "sli", "awbDoc", "certificates", "msds"],
    "PER": ["invoice", "packingList", "sli", "awbDoc", "certificates"],
    "HUM": ["invoice", "packingList", "sli", "awbDoc", "certificates"],
    "AVI": ["invoice", "packingList", "sli", "awbDoc", "certificates"],
    "VAL": ["invoice", "packingList", "sli", "awbDoc", "certificates"],
}

# ----------------------
# REGLAS DE VALIDACIÓN POR DOCUMENTO
# ----------------------
def validar_documento(doc: Documento, cargo_type: str) -> Documento:
    # Aquí se pueden añadir reglas Avianca-first
    if doc.status == "❌ Faltante":
        doc.comment = "Documento requerido según tipo de carga"
    elif doc.name == "msds" and cargo_type != "DG":
        doc.comment = "MSDS solo obligatorio para DG"
    elif doc.name == "certificates" and cargo_type not in ["DG","PER","HUM","AVI","VAL"]:
        doc.comment = "Certificado no requerido para este tipo de carga"
    return doc

# ----------------------
# MOTOR DE VALIDACIÓN DE CARGA
# ----------------------
def validar_carga(carga: Carga) -> ResultadoValidacion:
    docs_status: List[Documento] = []
    tipo = carga.cargo_type
    docs_obligatorios = REQUIRED_DOCS.get(tipo, REQUIRED_DOCS["GEN"])
    aceptable = True
    reason = ""

    # Revisar cada documento obligatorio
    for doc_name in docs_obligatorios:
        doc = next((d for d in carga.documents if d.name == doc_name), None)
        if doc is None:
            doc = Documento(
                name=doc_name,
                status="❌ Faltante",
                comment="Debe subir este documento",
                upload_date=datetime.now()
            )
            aceptable = False
        else:
            doc = validar_documento(doc, tipo)
            if doc.status != "✔ Válido":
                aceptable = False
        docs_status.append(doc)

    # Semáforo operativo
    if aceptable:
        status = "🟢 LISTA PARA ACEPTACIÓN"
    else:
        status = "🔴 NO ACEPTABLE"
        reason = "Documentos faltantes o inválidos según reglas Avianca"

    return ResultadoValidacion(
        status=status,
        documents=docs_status,
        reason=reason,
        timestamp=datetime.now()
    )

# ----------------------
# EJEMPLO: función para validar documentos de país destino
# ----------------------
DESTINATION_RULES = {
    "COL": ["invoice", "packingList", "sli", "awbDoc"],  # ejemplo simple
    "USA": ["invoice", "packingList", "sli", "awbDoc", "permits"],
    "BRA": ["invoice", "packingList", "sli", "awbDoc", "permits"],
}

def validar_por_pais(carga: Carga) -> ResultadoValidacion:
    docs_status: List[Documento] = []
    docs_obligatorios = DESTINATION_RULES.get(carga.destination.upper(), REQUIRED_DOCS.get(carga.cargo_type, []))
    aceptable = True
    reason = ""

    for doc_name in docs_obligatorios:
        doc = next((d for d in carga.documents if d.name == doc_name), None)
        if doc is None:
            doc = Documento(
                name=doc_name,
                status="❌ Faltante",
                comment="Documento requerido por país destino",
                upload_date=datetime.now()
            )
            aceptable = False
        docs_status.append(doc)

    status = "🟢 LISTA PARA ACEPTACIÓN" if aceptable else "🔴 NO ACEPTABLE"
    if not aceptable:
        reason = "Faltan documentos obligatorios para país destino"

    return ResultadoValidacion(
        status=status,
        documents=docs_status,
        reason=reason,
        timestamp=datetime.now()
    )
