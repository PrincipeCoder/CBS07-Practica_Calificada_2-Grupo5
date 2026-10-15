"""
Repositorio de transferencias (FinanUNI_Sec).
Implementa consultas 100% parametrizadas (RF05) y delimitación estricta de alcance en el servidor.
"""
from app.database.db import get_db_connection

def find_by_id(transfer_id: int):
    """
    Recupera los datos de una transferencia mediante consulta parametrizada segura.
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

def filter_transfers(enforced_user_id=None, is_auditor=False, target_client_id=None,
                     date_from=None, date_to=None, min_centimos=None, max_centimos=None):
    """
    Realiza la consulta de movimientos aplicando estrictamente consultas parametrizadas.
    
    ========================================================================================
    CONTROL DE SEGURIDAD (RF05 / RN04 - PARAMETRIZACIÓN Y ALCANCE EN SERVIDOR):
    1. Ningún valor externo se concatena en la cadena SQL; todos usan marcadores '?'.
    2. Si el solicitante es un cliente (is_auditor=False), el servidor FUERZA el alcance
       a sus propias cuentas (enforced_user_id), ignorando cualquier intento de suplantación.
    3. Si el solicitante es auditor (is_auditor=True), puede filtrar opcionalmente por cliente
       utilizando un parámetro '?' debidamente validado como entero.
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
    params = []

    if not is_auditor:
        # Alcance forzado en servidor para clientes: solo transferencias donde participan
        base_sql += " AND (co.titular_usuario_id = ? OR cd.titular_usuario_id = ?)"
        params.extend([enforced_user_id, enforced_user_id])
    else:
        # El auditor puede especificar un cliente_id si lo desea, enlazado como parámetro '?'
        if target_client_id is not None:
            base_sql += " AND (co.titular_usuario_id = ? OR cd.titular_usuario_id = ?)"
            params.extend([target_client_id, target_client_id])

    if date_from:
        base_sql += " AND t.fecha_utc >= ?"
        params.append(f"{date_from} 00:00:00")
    if date_to:
        base_sql += " AND t.fecha_utc <= ?"
        params.append(f"{date_to} 23:59:59")
    if min_centimos is not None:
        base_sql += " AND t.monto_centimos >= ?"
        params.append(min_centimos)
    if max_centimos is not None:
        base_sql += " AND t.monto_centimos <= ?"
        params.append(max_centimos)

    base_sql += " ORDER BY t.fecha_utc DESC LIMIT 100;"

    cursor.execute(base_sql, tuple(params))
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
