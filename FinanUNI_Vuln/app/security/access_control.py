"""
Módulo de control de acceso y autorización: RBAC y comprobación de propiedad de recursos.
"""

def check_user_role(user_role: str, allowed_roles: list):
    """
    Comprueba si el rol del usuario pertenece al conjunto de roles autorizados para la acción.
    
    :param user_role: Rol del usuario autenticado ('cliente' o 'auditor').
    :param allowed_roles: Lista de roles con permiso para ejecutar la operación.
    :return: None en este molde estructural (no devolver True arbitrario).
    
    TODO: Aplicar principio de denegación por defecto (RN04). Permitir ejecución
    únicamente si user_role está explícitamente contenido en allowed_roles.
    """
    return None

def check_transfer_ownership(user_id: int, transfer_id: int):
    """
    Comprueba si un usuario cliente tiene derecho a consultar una transferencia específica,
    verificando si es titular de la cuenta origen o destino (control contra IDOR / AM02).
    
    :param user_id: Identificador del usuario que solicita la consulta.
    :param transfer_id: Identificador numérico de la transferencia.
    :return: None en este molde estructural.
    
    TODO: Consultar las cuentas asociadas a la transferencia y contrastarlas con
    las cuentas del usuario autenticado cargadas desde el servidor (no confiar en el cliente).
    """
    return None

def check_account_ownership(user_id: int, account_id: int):
    """
    Comprueba si la cuenta bancaria especificada pertenece al usuario activo.
    
    :param user_id: Identificador del usuario autenticado.
    :param account_id: Identificador de la cuenta bancaria origen.
    :return: None en este molde estructural.
    
    TODO: Validar en el repositorio que titular_usuario_id coincida con user_id
    antes de permitir débitos o transferencias desde dicha cuenta.
    """
    return None
