ROLES = {
    "owner": {"can_upload": True, "can_validate": False, "can_approve": False},
    "forwarder": {"can_upload": True, "can_validate": True, "can_approve": False},
    "driver": {"can_upload": False, "can_validate": True, "can_approve": False},
    "warehouse": {"can_upload": False, "can_validate": True, "can_approve": True},
    "admin": {"can_upload": True, "can_validate": True, "can_approve": True}
}

def get_role_permissions(role: str) -> dict:
    return ROLES.get(role.lower(), {"can_upload": False, "can_validate": False, "can_approve": False})
