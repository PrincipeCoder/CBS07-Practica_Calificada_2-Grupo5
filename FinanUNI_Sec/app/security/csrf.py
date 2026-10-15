"""
Módulo de protección contra Cross-Site Request Forgery (CSRF - AM08 / FinanUNI_Sec).
"""

def generate_csrf_token():
    """
    Genera un token CSRF criptográficamente seguro asociado a la sesión servidora.
    
    :return: None en este molde estructural.
    
    TODO: Generar token con secrets.token_hex(32) y persistirlo o vincularlo a la sesión activa.
    """
    return None

def validate_csrf_token(token_received: str, expected_token: str):
    """
    Valida en tiempo constante el token CSRF recibido contra el esperado.
    
    :param token_received: Token proporcionado en la cabecera o formulario.
    :param expected_token: Token almacenado en la sesión del usuario.
    :return: None en este molde estructural.
    
    TODO: Validar mediante hmac.compare_digest para prevenir ataques de temporización.
    """
    return None
