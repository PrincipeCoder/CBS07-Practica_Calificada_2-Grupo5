"""
Servicio de transferencias: lógica de coordinación, integración con motor C y consultas.
"""

def invoke_c_converter(monto_soles: int):
    """
    Invoca el binario C externo para la conversión de soles enteros a céntimos (RF08 / AM03).
    Aplica timeout de 1 segundo, ejecución sin shell y parseo seguro de la salida JSON.
    
    :param monto_soles: Cantidad de soles enteros a convertir.
    :return: None en este molde estructural.
    
    TODO: Ejecutar subproceso 'motor_c/conversor_c' pasando el argumento entero canónico,
    capturar respuesta JSON {'estado': 'OK', 'centimos': ...} y controlar códigos de salida.
    """
    return None

def process_transfer(user_id: int, cuenta_origen_id: int, cuenta_destino_id: int, monto_soles: int):
    """
    Coordina la secuencia transaccional de una transferencia financiera (RF09, RF10, RN08):
    1. Verificar sesión y autorización de rol.
    2. Comprobar que cuenta_origen_id pertenece al usuario y que origen != destino.
    3. Invocar motor C para conversión a céntimos.
    4. Comprobar saldo suficiente en origen y límite en cuenta destino.
    5. Aplicar débito, crédito, registro de transferencia y auditoría atómica en SQLite.
    
    :param user_id: ID del usuario autenticado que emite la orden.
    :param cuenta_origen_id: Cuenta de débito.
    :param cuenta_destino_id: Cuenta de crédito.
    :param monto_soles: Monto en soles enteros.
    :return: None en este molde estructural (no devolver éxito simulado).
    
    TODO: Orquestar la transacción atómica completa con rollback ante cualquier anomalía.
    """
    return None

def get_transfer_details(user_id: int, user_role: str, transfer_id: int):
    """
    Obtiene los detalles de una transferencia aplicando la política de autorización:
    - Cliente: solo si es titular de la cuenta origen o destino (mitigación IDOR en Sec).
    - Auditor: cualquier transferencia del sistema.
    
    :param user_id: ID del usuario solicitante.
    :param user_role: Rol del solicitante ('cliente' o 'auditor').
    :param transfer_id: ID de la transferencia a consultar.
    :return: None en este molde estructural.
    
    TODO: En FinanUNI_Vuln evidenciar la exposición directa (AB02); en FinanUNI_Sec retornar 404
    uniforme ante transferencias ajenas o inexistentes (AM02 / T05).
    """
    return None

def list_movements(user_id: int, user_role: str, filters: dict):
    """
    Consulta transferencias filtradas acotadas al alcance autorizado del usuario:
    - Cliente: únicamente operaciones donde participa (origen o destino).
    - Auditor: todas las transferencias de la base de datos.
    
    :param user_id: ID del usuario.
    :param user_role: Rol ('cliente' o 'auditor').
    :param filters: Criterios opcionales (cliente_id, fechas, montos).
    :return: None en este molde estructural.
    
    TODO: En FinanUNI_Vuln exponer concatenación de filtros (AM01 / T03); en FinanUNI_Sec
    aplicar parametrización estricta y alcance forzado en el servidor (RF05 / T04).
    """
    return None
