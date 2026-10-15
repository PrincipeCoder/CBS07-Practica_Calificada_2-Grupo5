"""
Fábrica de aplicaciones Flask para FinanUNI.
"""
from flask import Flask
from .config import Config, VulnConfig
from .routes.web_routes import web_bp
from .routes.api_routes import api_bp
from .database.db import close_db_connection

def create_app(config_class=VulnConfig):
    """
    Crea y configura una instancia de la aplicación Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Registrar Blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # Registrar cierre de base de datos
    app.teardown_appcontext(close_db_connection)

    # Procesador de contexto para plantillas
    @app.context_processor
    def inject_app_context():
        return {
            'app_name': app.config.get('APP_NAME', 'FinanUNI'),
            'app_port': app.config.get('PORT', 5000),
            'is_vulnerable': app.config.get('IS_VULNERABLE', False),
            'peer_app_url': app.config.get('PEER_APP_URL', 'http://127.0.0.1:5001'),
            'peer_app_name': app.config.get('PEER_APP_NAME', 'FinanUNI_Sec')
        }

    return app
