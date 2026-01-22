from models import Usuario, Carga, ResultadoValidacion

ROLE_PERMISSIONS = {
    "owner": ["view_status", "view_risks"],
    "forwarder": ["view_missing_docs", "precheck"],
    "truck_driver": ["go_or_not"],
    "warehouse": ["accept_reject", "hold"],
    "admin": ["manage_rules", "audit_logs"]
}

def can(user: Usuario, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(user.role, [])

def view_for_role(user: Usuario, resultado: ResultadoValidacion):
    """
    Devuelve solo la información relevante según rol
    """
    if user.role == "owner":
        return {
            "status": resultado.status,
            "reason": resultado.reason,
            "timestamp": resultado.timestamp
        }
    elif user.role == "forwarder":
        missing_docs = [d for d in resultado.documents if d.status != "✔ Válido"]
        return {
            "missing_documents": missing_docs,
            "status": resultado.status,
            "timestamp": resultado.timestamp
        }
    elif user.role == "truck_driver":
        can_go = resultado.status == "🟢 LISTA PARA ACEPTACIÓN"
        return {"go_or_not": can_go, "status": resultado.status}
    elif user.role == "warehouse":
        return {
            "documents": resultado.documents,
            "status": resultado.status,
            "reason": resultado.reason
        }
    elif user.role == "admin":
        return resultado.dict()
    else:
        return {"status": resultado.status}
