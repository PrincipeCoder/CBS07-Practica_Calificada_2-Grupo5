"""
Repositorio de cuentas bancarias (FinanUNI_Vuln).
Operaciones de consulta y persistencia de cuentas y saldos en céntimos.
"""
from app.database.db import get_db_connection

def find_by_id(account_id: int):
    """
    Busca una cuenta bancaria por su identificador numérico.
    """
    if not account_id:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titular_usuario_id, saldo_centimos 
        FROM cuentas 
        WHERE id = ?;
    """, (account_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def find_by_user_id(user_id: int):
    """
    Obtiene todas las cuentas bancarias pertenecientes a un titular.
    """
    if not user_id:
        return []
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titular_usuario_id, saldo_centimos 
        FROM cuentas 
        WHERE titular_usuario_id = ?;
    """, (user_id,))
    return [dict(r) for r in cursor.fetchall()]

def update_balance_atomic(account_id: int, delta_centimos: int, connection=None):
    """
    Actualiza el saldo de una cuenta dentro de una transacción.
    
    Comprobamos que el nuevo saldo no sea negativo ni exceda el límite int32_t (2147483647).
    Si se viola la condición, lanzamos ValueError para forzar rollback de la transacción.
    """
    conn = connection or get_db_connection()
    cursor = conn.cursor()
    
    # Leemos saldo actual
    cursor.execute("SELECT saldo_centimos FROM cuentas WHERE id = ?;", (account_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Cuenta {account_id} inexistente.")
    
    nuevo_saldo = row['saldo_centimos'] + delta_centimos
    if nuevo_saldo < 0:
        raise ValueError(f"Saldo insuficiente en cuenta {account_id} (saldo actual: {row['saldo_centimos']} céntimos).")
    if nuevo_saldo > 2147483647:
        raise ValueError(f"El saldo resultante en cuenta {account_id} excedería el límite de INT32_MAX.")
    
    cursor.execute("UPDATE cuentas SET saldo_centimos = ? WHERE id = ?;", (nuevo_saldo, account_id))
    return nuevo_saldo
