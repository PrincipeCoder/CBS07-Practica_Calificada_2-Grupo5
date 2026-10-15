"""
Módulo de auditoría: registro seguro de eventos (RF11 / AM05).
Registra actor, acción, recurso, resultado y correlación; excluye contraseñas y secretos.
"""

def log_security_event(actor: str, accion: str, recurso: str, resultado: str,
                       motivo: str = None, correlacion_id: str = None):
    """
    Registra un evento estructurado de auditoría en la base de datos y log local.
    
    :param actor: Identificador del actor ('anonimo', 'cliente:1', 'auditor:3').
    :param accion: Operación efectuada (ej. 'LOGIN', 'LOGOUT', 'TRANSFER', 'QUERY_MOVEMENTS').
    :param recurso: Recurso involucrado (ej. 'auth', 'transfer:1051', 'account:101').
    :param resultado: 'EXITO', 'RECHAZO' o 'FALLO'.
    :param motivo: Detalle normalizado del rechazo o falla.
    :param correlacion_id: Identificador único UUID para trazabilidad de la petición.
    :return: None en este molde estructural.
    
    TODO: Insertar evento estructurado en tabla 'eventos_auditoria' y registrar en archivo de log,
    garantizando que ninguna contraseña, cookie de sesión o dato secreto sea registrado.
    """
    return None

def get_recent_audit_events(limit: int = 100):
    """
    Recupera los eventos recientes de auditoría para consulta por el auditor.
    
    :param limit: Cantidad máxima de registros a recuperar.
    :return: None en este molde estructural.
    
    TODO: Consultar tabla 'eventos_auditoria' ordenados por fecha_utc descendente.
    """
    return None
