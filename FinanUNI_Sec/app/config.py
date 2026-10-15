"""
FinanUNI_Sec - Módulo de Configuración
Define los parámetros de entorno y ejecución de la aplicación segura.
"""
import os

class Config:
    """Configuración base de FinanUNI."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_change_in_production')
    DEBUG = False
    TESTING = False
    APP_NAME = "FinanUNI_Sec"
    PORT = 5001
    HOST = "127.0.0.1"
    SESSION_COOKIE_NAME = "finanuni_sec_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    DATABASE_PATH = os.path.join("instance", "finanuni_sec.db")
    PEER_APP_URL = "http://127.0.0.1:5000"
    PEER_APP_NAME = "FinanUNI_Vuln"
    IS_VULNERABLE = False

class SecConfig(Config):
    """Configuración específica para la instancia FinanUNI_Sec (Puerto 5001)."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_sec_secret_key_academic_only')
    DEBUG = True
    APP_NAME = "FinanUNI_Sec"
    PORT = 5001
    SESSION_COOKIE_NAME = "finanuni_sec_session"
    DATABASE_PATH = os.path.join("instance", "finanuni_sec.db")
    PEER_APP_URL = "http://127.0.0.1:5000"
    PEER_APP_NAME = "FinanUNI_Vuln"
    IS_VULNERABLE = False
