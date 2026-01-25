from fastapi import HTTPException
from typing import List

# Roles definidos
class UserRole:
    SHIPPER = "Shipper"
    FORWARDER = "Forwarder"
    CHOFER = "Chofer"
    WAREHOUSE = "Warehouse"
    OPERADOR = "Operador"
    DESTINATARIO = "Destinatario"

# Verificar rol de usuario
def verify_user(role: str, allowed_roles: List[str]):
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Access denied for this role")
    return True
