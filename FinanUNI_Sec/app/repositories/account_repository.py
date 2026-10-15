"""
Repositorio de cuentas bancarias (FinanUNI_Sec).
Operaciones de consulta y persistencia atómica de saldos en céntimos con verificación de límites.
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
    
    Verificamos las invariantes contables:
    - Saldo final >= 0 (no sobregiro).
    - Saldo final <= 2,147,483,647 céntimos (límite int32_t sin overflow).
    """
    conn = connection or get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT saldo_centimos FROM cuentas WHERE id = ?;", (account_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Cuenta {account_id} inexistente.")
    
    nuevo_saldo = row['saldo_centimos'] + delta_centimos
    if nuevo_saldo < 0:
        raise ValueError(f"Saldo insuficiente en cuenta {account_id}.")
    if nuevo_saldo > 2147483647:
        raise ValueError(f"El saldo excede el límite permitido para cuenta {account_id}.")
    
    cursor.execute("UPDATE cuentas SET saldo_centimos = ? WHERE id = ?;", (nuevo_saldo, account_id))
    return nuevo_saldo
