"""
Servicio de autenticación y gestión de sesiones servidoras (FinanUNI_Vuln).
Implementa sesiones opacas con caducidad en servidor y contraseñas protegidas con Argon2id.
"""
import secrets
from datetime import datetime, timedelta, timezone
from app.database.db import get_db_connection
from app.repositories import user_repository
from app.security.crypto import verify_password

def authenticate_user(username: str, plain_password: str):
    """
    Verifica las credenciales del usuario y genera una sesión opaca servidora.
    
    Comprobamos si el usuario existe y está activo:
    - Si el usuario no existe o la contraseña no coincide con el hash Argon2id,
      retornamos (None, "Credenciales inválidas") con mensaje genérico para evitar
      revelar si el usuario existe o no (defensa contra enumeración de cuentas).
    - Si las credenciales son válidas, generamos un identificador de sesión opaco
      criptográficamente aleatorio y lo registramos en la tabla 'sesiones' con 30 minutos de vida.
    """
    if not username or not plain_password:
        return None, "Debe proporcionar usuario y contraseña."
    
    user = user_repository.find_by_username(username.strip())
    if not user or user.get('activo') != 1:
        return None, "Credenciales inválidas."
    
    # Verificación en tiempo constante contra el hash Argon2id
    if not verify_password(plain_password, user['password_hash']):
        return None, "Credenciales inválidas."
    
    # Generar sesión en el servidor
    token = create_session_record(user['id'])
    return user, token

def create_session_record(user_id: int) -> str:
    """
    Crea un identificador opaco aleatorio (64 hex) y lo almacena con expiración UTC (+30 min).
    """
    session_id = secrets.token_hex(32)
    expiracion = (datetime.now(timezone.utc) + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sesiones (id, usuario_id, expiracion, estado)
        VALUES (?, ?, ?, 'activa');
    """, (session_id, user_id, expiracion))
    conn.commit()
    return session_id

def validate_active_session(session_token: str):
    """
    Comprueba si el identificador opaco corresponde a una sesión activa y no expirada en el servidor.
    
    Verificamos:
    1. Si el token existe en la tabla 'sesiones'.
    2. Si el estado es exactamente 'activa'.
    3. Si la fecha actual en UTC es anterior a la fecha de expiración almacenada.
       Si ya expiró, actualizamos su estado a 'expirada' y retornamos None.
    4. Que el usuario titular siga activo en el sistema.
    """
    if not session_token:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.usuario_id, s.expiracion, s.estado, u.nombre_acceso, u.rol, u.activo
        FROM sesiones s
        JOIN usuarios u ON s.usuario_id = u.id
        WHERE s.id = ?;
    """, (session_token,))
    row = cursor.fetchone()
    
    if not row:
        return None
    
    if row['estado'] != 'activa' or row['activo'] != 1:
        return None
    
    ahora_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    if row['expiracion'] < ahora_utc:
        # La sesión ha caducado por inactividad
        cursor.execute("UPDATE sesiones SET estado = 'expirada' WHERE id = ?;", (session_token,))
        conn.commit()
        return None
    
    return {
        'id': row['usuario_id'],
        'nombre_acceso': row['nombre_acceso'],
        'rol': row['rol'],
        'session_id': row['id']
    }

def logout_session(session_token: str) -> bool:
    """
    Invalida y revoca la sesión en la base de datos servidora.
    """
    if not session_token:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sesiones SET estado = 'revocada' WHERE id = ?;", (session_token,))
    conn.commit()
    return True
