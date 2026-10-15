"""
Repositorio de transferencias (FinanUNI_Vuln).
Contiene la consulta de transferencias y la vulnerabilidad deliberada de SQL Injection en filter_transfers.
"""
from app.database.db import get_db_connection

def find_by_id(transfer_id: int):
    """
    Recupera los datos completos de una transferencia por su identificador.
    """
    if not transfer_id:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.cuenta_origen_id, t.cuenta_destino_id, t.monto_centimos, t.fecha_utc,
               co.titular_usuario_id AS titular_origen_id, uo.nombre_acceso AS titular_origen,
               cd.titular_usuario_id AS titular_destino_id, ud.nombre_acceso AS titular_destino
        FROM transferencias t
        JOIN cuentas co ON t.cuenta_origen_id = co.id
        JOIN usuarios uo ON co.titular_usuario_id = uo.id
        JOIN cuentas cd ON t.cuenta_destino_id = cd.id
        JOIN usuarios ud ON cd.titular_usuario_id = ud.id
        WHERE t.id = ?;
    """, (transfer_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def filter_transfers(client_id=None, date_from=None, date_to=None, min_centimos=None, max_centimos=None):
    """
    Realiza la consulta de movimientos filtrados.
    
    ========================================================================================
    DEFECTO DELIBERADO (VULNERABILIDAD ACADÉMICA AM01 / CWE-89 - SQL INJECTION):
    En esta versión de laboratorio concatenamos directamente el valor del filtro 'client_id'
    dentro de la sentencia SQL en lugar de usar parámetros enlazados (?).
    
    - Solicitud legítima: client_id = "1" -> filtra las transferencias del cliente 1 (Ana).
    - Solicitud maliciosa: client_id = "1 OR 1=1" -> inyecta una condición tautológica que
      altera la lógica de selección y extrae transferencias de todos los clientes de la base.
    ========================================================================================
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    base_sql = """
        SELECT t.id, t.cuenta_origen_id, t.cuenta_destino_id, t.monto_centimos, t.fecha_utc,
               uo.nombre_acceso AS titular_origen, ud.nombre_acceso AS titular_destino
        FROM transferencias t
        JOIN cuentas co ON t.cuenta_origen_id = co.id
        JOIN usuarios uo ON co.titular_usuario_id = uo.id
        JOIN cuentas cd ON t.cuenta_destino_id = cd.id
        JOIN usuarios ud ON cd.titular_usuario_id = ud.id
        WHERE 1=1
    """

    # PUNTO VULNERABLE: Concatenación directa del parámetro recibido
    if client_id is not None and str(client_id).strip() != "":
        raw_client = str(client_id).strip()
        base_sql += f" AND (co.titular_usuario_id = {raw_client} OR cd.titular_usuario_id = {raw_client})"

    if date_from:
        base_sql += f" AND t.fecha_utc >= '{date_from}'"
    if date_to:
        base_sql += f" AND t.fecha_utc <= '{date_to} 23:59:59'"
    if min_centimos is not None:
        base_sql += f" AND t.monto_centimos >= {min_centimos}"
    if max_centimos is not None:
        base_sql += f" AND t.monto_centimos <= {max_centimos}"

    base_sql += " ORDER BY t.fecha_utc DESC LIMIT 100;"

    cursor.execute(base_sql)
    return [dict(r) for r in cursor.fetchall()]

def create_transfer(cuenta_origen_id: int, cuenta_destino_id: int, monto_centimos: int, connection=None):
    """
    Inserta una transferencia dentro de una transacción activa.
    """
    from datetime import datetime, timezone
    conn = connection or get_db_connection()
    cursor = conn.cursor()
    fecha_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO transferencias (cuenta_origen_id, cuenta_destino_id, monto_centimos, fecha_utc)
        VALUES (?, ?, ?, ?);
    """, (cuenta_origen_id, cuenta_destino_id, monto_centimos, fecha_utc))
    return cursor.lastrowid
