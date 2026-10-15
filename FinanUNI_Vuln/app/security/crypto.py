"""
Módulo criptográfico: funciones de hash y verificación de contraseñas.
Implementa Argon2id para el almacenamiento seguro de credenciales según el requisito RN05.
Tanto la versión vulnerable como la versión segura comparten esta implementación
para aislar los defectos exclusivamente en los puntos de demostración asignados.
"""
import logging
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# Instancia global del derivador de claves Argon2id con parámetros estándar
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
    
    :param plain_password: La contraseña enviada por el usuario.
    :return: Cadena con el hash codificado que incluye algoritmo, versión, costo y sal.
    """
    if not plain_password:
        raise ValueError("La contraseña no puede estar vacía para generar el hash.")
    return _hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Comprueba si la contraseña en texto plano coincide con el hash Argon2id almacenado.
    
    Comprobamos si el hash coincide de forma resistente a ataques de temporización:
    - Si coincide, verify() retorna True sin lanzar excepción.
    - Si no coincide o el formato es incorrecto, capturamos VerifyMismatchError/InvalidHashError
      y retornamos False para evitar caídas no controladas o mensajes que revelen detalles internos.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        # La contraseña no coincide o el hash está corrupto
        return False
    except Exception as e:
        logging.error("Error inesperado verificando contraseña: %s", type(e).__name__)
        return False
