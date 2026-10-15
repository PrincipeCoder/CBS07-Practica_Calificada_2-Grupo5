"""
Rutas de API REST de FinanUNI.
En este avance de estructura, los endpoints de negocio responden explícitamente con HTTP 501
y el mensaje 'Funcionalidad pendiente de implementación', sin simular operaciones.
El endpoint de salud responde con HTTP 200 informando el estado básico de la infraestructura.
"""
from flask import Blueprint, jsonify, request, current_app

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de salud básico de la aplicación.
    Verifica que la instancia Flask esté en ejecución y responda peticiones.
    """
    return jsonify({
        "status": "ok",
        "app": current_app.config.get('APP_NAME'),
        "port": current_app.config.get('PORT'),
        "is_vulnerable_app": current_app.config.get('IS_VULNERABLE', False),
        "stage": "molde_inicial",
        "message": "Servidor Flask activo y operativo. Módulos de negocio pendientes de implementación."
    }), 200

@api_bp.route('/login', methods=['POST'])
def api_login():
    """
    Endpoint pendiente de autenticación (RF02 / AM04).
    Retorna explícitamente HTTP 501 sin crear sesión ni autenticar usuarios.
    """
    return jsonify({
        "status": "pending",
        "codigo": 501,
        "mensaje": "Funcionalidad pendiente de implementación",
        "detalle": "La autenticación y gestión de sesiones se implementarán en la siguiente etapa."
    }), 501

@api_bp.route('/logout', methods=['POST'])
def api_logout():
    """
    Endpoint pendiente de cierre de sesión (RN05).
    Retorna explícitamente HTTP 501.
    """
    return jsonify({
        "status": "pending",
        "codigo": 501,
        "mensaje": "Funcionalidad pendiente de implementación",
        "detalle": "La revocación de sesiones se implementará en la siguiente etapa."
    }), 501

@api_bp.route('/movimientos', methods=['GET'])
def api_movimientos():
    """
    Endpoint pendiente de consulta de movimientos (RF04, RF05 / AM01).
    Retorna explícitamente HTTP 501 sin ejecutar consultas a base de datos.
    """
    return jsonify({
        "status": "pending",
        "codigo": 501,
        "mensaje": "Funcionalidad pendiente de implementación",
        "detalle": "La consulta de movimientos y filtros se implementará en la siguiente etapa."
    }), 501

@api_bp.route('/transferencias/<id>', methods=['GET'])
def api_detalle_transferencia(id):
    """
    Endpoint pendiente de detalle de transferencia (RF06 / AM02).
    Retorna explícitamente HTTP 501 sin consultar registros.
    """
    return jsonify({
        "status": "pending",
        "codigo": 501,
        "id_solicitado": id,
        "mensaje": "Funcionalidad pendiente de implementación",
        "detalle": "El detalle de transferencias y control de acceso por recurso se implementará en la siguiente etapa."
    }), 501

@api_bp.route('/transferencias', methods=['POST'])
def api_crear_transferencia():
    """
    Endpoint pendiente de creación de transferencias (RF08, RF09, RF10 / AM03, AM07).
    Retorna explícitamente HTTP 501 sin alterar saldos ni registrar transferencias.
    """
    return jsonify({
        "status": "pending",
        "codigo": 501,
        "mensaje": "Funcionalidad pendiente de implementación",
        "detalle": "La orquestación de transferencias, conversión en C y persistencia atómica se implementará en la siguiente etapa."
    }), 501
