"""
Módulo de control de acceso y autorización (FinanUNI_Sec).
Aplica RBAC y control de acceso a nivel de objeto/recurso con denegación por defecto (RN04 / RF06 / RF07).
"""
from app.repositories import account_repository

def check_user_role(user_role: str, allowed_roles: list) -> bool:
    """
    Comprueba si el rol del usuario pertenece a los roles permitidos.
    Aplica principio de denegación por defecto: si no está explícitamente en la lista, retorna False.
    """
    if not user_role or not allowed_roles:
        return False
    return user_role in allowed_roles

def check_transfer_participation(user_id: int, transfer: dict) -> bool:
    """
    Comprueba si el usuario cliente participa en la transferencia como titular del origen o del destino.
    
    ========================================================================================
    CONTROL DE SEGURIDAD (AM02 / RF06 - MITIGACIÓN DE IDOR):
    Verificamos la pertenencia del recurso cruzando el ID del usuario autenticado cargado
    del servidor con los titulares de las cuentas participantes.
    ========================================================================================
    """
    if not user_id or not transfer:
        return False
    
    es_origen = transfer.get('titular_origen_id') == user_id
    es_destino = transfer.get('titular_destino_id') == user_id
    return es_origen or es_destino

def check_account_ownership(user_id: int, account_id: int) -> bool:
    """
    Comprueba si una cuenta bancaria pertenece al usuario autenticado.
    Evita que un cliente ordene transferencias desde cuentas ajenas (AB04).
    """
    if not user_id or not account_id:
        return False
    account = account_repository.find_by_id(account_id)
    if not account:
        return False
    return account['titular_usuario_id'] == user_id
