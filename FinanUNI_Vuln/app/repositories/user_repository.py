"""
Repositorio de usuarios (FinanUNI_Vuln).
Operaciones de lectura y persistencia de cuentas de acceso.
"""
from app.database.db import get_db_connection

def find_by_username(username: str):
    """
    Busca un usuario por su nombre de acceso único.
    
    Comprobamos si el nombre existe en la tabla 'usuarios':
    - Si existe, retornamos un diccionario con sus atributos (incluyendo rol y password_hash).
    - Si no existe, retornamos None para indicar que el usuario no fue hallado.
    """
    if not username:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre_acceso, password_hash, rol, activo 
        FROM usuarios 
        WHERE nombre_acceso = ?;
    """, (username,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def find_by_id(user_id: int):
    """
    Busca un usuario por su identificador primario numérico.
    """
    if not user_id:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre_acceso, password_hash, rol, activo 
        FROM usuarios 
        WHERE id = ?;
    """, (user_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None
