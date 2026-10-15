"""
Servicio de cuentas bancarias (FinanUNI_Sec): consulta autorizada de balances y cuentas del titular.
"""

def get_account_for_user(account_id: int, user_id: int, user_role: str):
    """
    Obtiene los datos de la cuenta verificando autorización según rol y propiedad.
    
    :param account_id: ID de la cuenta bancaria.
    :param user_id: ID del usuario solicitante.
    :param user_role: Rol del usuario solicitante.
    :return: None en este molde estructural.
    
    TODO: Permitir consulta si el usuario es el titular legítimo o si posee rol auditor.
    """
    return None

def get_user_accounts(user_id: int):
    """
    Lista las cuentas asociadas a un usuario titular cliente.
    
    :param user_id: ID del cliente autenticado.
    :return: None en este molde estructural.
    
    TODO: Consultar repositorio de cuentas y formatear para vista de usuario.
    """
    return None
