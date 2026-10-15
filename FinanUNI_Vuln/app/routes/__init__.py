"""
Módulo de rutas de FinanUNI: rutas web de interfaz y rutas de API REST.
"""
from .web_routes import web_bp
from .api_routes import api_bp

__all__ = ['web_bp', 'api_bp']
