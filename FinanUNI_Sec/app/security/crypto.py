"""
Módulo criptográfico: funciones de hash y verificación de contraseñas (FinanUNI_Sec).
Implementa Argon2id para el almacenamiento seguro de credenciales según el requisito RN05.
"""
import logging
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# Parámetros recomendados para mitigar ataques de fuerza bruta mediante GPU/ASIC
_hasher = PasswordHasher(
    time_cost=3,        # 3 iteraciones
    memory_cost=65536,  # 64 MiB de memoria
    parallelism=4,      # 4 hilos paralelos
    hash_len=32,
    salt_len=16
)

def hash_password(plain_password: str) -> str:
    """
    Genera un hash seguro para la contraseña en texto plano utilizando Argon2id.
    """
    if not plain_password:
        raise ValueError("La contraseña no puede estar vacía para generar el hash.")
    return _hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Comprueba si la contraseña coincide con el hash almacenado en tiempo constante.
    
    Verificamos el hash con Argon2id. Si hay discrepancia, se captura la excepción
    y devolvemos False sin propagar trazas ni detalles que ayuden a un atacante.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    except Exception as e:
        logging.error("Error inesperado verificando contraseña en Sec: %s", type(e).__name__)
        return False
