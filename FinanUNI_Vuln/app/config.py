"""
FinanUNI - Módulo de Configuración
Define los parámetros de entorno y ejecución de la aplicación.
"""
import os

class Config:
    """Configuración base de FinanUNI."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_change_in_production')
    DEBUG = False
    TESTING = False
    APP_NAME = "FinanUNI"
    PORT = 5000
    HOST = "127.0.0.1"
    SESSION_COOKIE_NAME = "finanuni_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    DATABASE_PATH = os.path.join("instance", "finanuni.db")
    PEER_APP_URL = "http://127.0.0.1:5001"
    PEER_APP_NAME = "FinanUNI_Sec"
    IS_VULNERABLE = False

class VulnConfig(Config):
    """Configuración específica para la instancia FinanUNI_Vuln (Puerto 5000)."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_vuln_secret_key_academic_only')
    DEBUG = True
    APP_NAME = "FinanUNI_Vuln"
    PORT = 5000
    SESSION_COOKIE_NAME = "finanuni_vuln_session"
    DATABASE_PATH = os.path.join("instance", "finanuni_vuln.db")
    PEER_APP_URL = "http://127.0.0.1:5001"
    PEER_APP_NAME = "FinanUNI_Sec"
    IS_VULNERABLE = True
