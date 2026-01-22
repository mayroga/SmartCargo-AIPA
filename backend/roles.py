# backend/roles.py

ROLES = {
    "agent": {
        "can_upload": True,
        "can_validate": False,
        "can_approve": False
    },
    "airline": {
        "can_upload": False,
        "can_validate": True,
        "can_approve": True
    },
    "auditor": {
        "can_upload": False,
        "can_validate": False,
        "can_approve": False
    }
}


def get_role_permissions(role: str) -> dict:
    """
    Devuelve permisos según rol.
    Rol desconocido = solo lectura
    """
    return ROLES.get(role, {
        "can_upload": False,
        "can_validate": False,
        "can_approve": False
    })
