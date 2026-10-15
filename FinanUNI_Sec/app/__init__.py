"""
Fábrica de aplicaciones Flask para FinanUNI_Sec.
"""
import os
from flask import Flask, request
from .config import Config, SecConfig
from .routes.web_routes import web_bp
from .routes.api_routes import api_bp
from .database.db import close_db_connection, init_db, load_seed_data
from .services import auth_service
from .security import csrf

def create_app(config_class=SecConfig):
    """
    Crea y configura una instancia de la aplicación Flask para FinanUNI_Sec.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Registrar Blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # Registrar cierre de base de datos
    app.teardown_appcontext(close_db_connection)

    # Inicializar y sembrar base de datos si no existe
    with app.app_context():
        db_path = app.config.get('DATABASE_PATH')
        if not os.path.exists(db_path):
            init_db()
            load_seed_data()

    # Procesador de contexto para plantillas
    @app.context_processor
    def inject_app_context():
        cookie_name = app.config.get('SESSION_COOKIE_NAME', 'finanuni_sec_session')
        session_token = request.cookies.get(cookie_name)
        user = auth_service.validate_active_session(session_token) if session_token else None
        token_csrf = csrf.generate_csrf_token(session_token) if user else ''
        
        return {
            'app_name': app.config.get('APP_NAME', 'FinanUNI_Sec'),
            'app_port': app.config.get('PORT', 5001),
            'is_vulnerable': app.config.get('IS_VULNERABLE', False),
            'peer_app_url': app.config.get('PEER_APP_URL', 'http://127.0.0.1:5000'),
            'peer_app_name': app.config.get('PEER_APP_NAME', 'FinanUNI_Vuln'),
            'current_user': user,
            'csrf_token': token_csrf
        }

    return app
