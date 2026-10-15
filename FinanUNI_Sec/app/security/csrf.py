"""
Módulo de protección contra Cross-Site Request Forgery (CSRF - AM08 / FinanUNI_Sec).
Genera y valida tokens CSRF vinculados criptográficamente a la sesión servidora activa.
"""
import hmac
import hashlib
from flask import current_app

def generate_csrf_token(session_id: str) -> str:
    """
    Genera un token CSRF derivado de la clave secreta y el identificador de sesión.
    """
    if not session_id:
        return ""
    secret = current_app.config.get('SECRET_KEY', 'default_secret').encode('utf-8')
    token = hmac.new(secret, session_id.encode('utf-8'), hashlib.sha256).hexdigest()
    return token

def validate_csrf_token(session_id: str, token_received: str) -> bool:
    """
    Comprueba el token CSRF recibido contra el derivado de la sesión en tiempo constante.
    
    Verificamos:
    - Que el token recibido no sea nulo ni vacío.
    - Comparamos mediante hmac.compare_digest para prevenir ataques de canal lateral por temporización.
    """
    if not session_id or not token_received:
        return False
    expected = generate_csrf_token(session_id)
    return hmac.compare_digest(expected, token_received.strip())
