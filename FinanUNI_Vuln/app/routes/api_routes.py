"""
Rutas de API REST de FinanUNI_Vuln (Puerto 5000).
Implementa endpoints funcionales para autenticación, consulta de movimientos (con SQLi)
y detalle de transferencias (con IDOR).
"""
from flask import Blueprint, jsonify, request, current_app, make_response
from app.services import auth_service, transfer_service

api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_authenticated_user():
    """
    Recupera el usuario autenticado a partir de la cookie de sesión del servidor.
    """
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'finanuni_vuln_session')
    session_token = request.cookies.get(cookie_name)
    if not session_token:
        return None
    return auth_service.validate_active_session(session_token)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servidor."""
    return jsonify({
        "status": "ok",
        "app": current_app.config.get('APP_NAME'),
        "port": current_app.config.get('PORT'),
        "is_vulnerable_app": True,
        "stage": "etapa_5",
        "message": "Servidor activo. Autenticación, SQLi e IDOR disponibles para demostración académica."
    }), 200

@api_bp.route('/login', methods=['POST'])
def api_login():
    """
    Autenticación funcional de usuarios mediante sesiones opacas en base de datos.
    """
    data = request.get_json(silent=True) or request.form
    username = data.get('nombre_acceso') or data.get('username')
    password = data.get('password')

    user, token_or_err = auth_service.authenticate_user(username, password)
    if not user:
        return jsonify({
            "status": "error",
            "codigo": 401,
            "error": token_or_err
        }), 401

    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'finanuni_vuln_session')
    response = make_response(jsonify({
        "status": "ok",
        "mensaje": "Inicio de sesión correcto.",
        "usuario": {
            "id": user['id'],
            "nombre_acceso": user['nombre_acceso'],
            "rol": user['rol']
        }
    }), 200)

    # Establecemos la cookie HttpOnly y SameSite=Lax
    response.set_cookie(
        cookie_name,
        token_or_err,
        httponly=True,
        samesite='Lax'
    )
    return response

@api_bp.route('/logout', methods=['POST'])
def api_logout():
    """
    Cierre de sesión e invalidación del token en el servidor.
    """
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'finanuni_vuln_session')
    token = request.cookies.get(cookie_name)
    if token:
        auth_service.logout_session(token)

    response = make_response(jsonify({
        "status": "ok",
        "mensaje": "Sesión cerrada correctamente."
    }), 200)
    response.delete_cookie(cookie_name)
    return response

@api_bp.route('/me', methods=['GET'])
def api_me():
    """Retorna los datos del usuario actualmente autenticado."""
    user = get_authenticated_user()
    if not user:
        return jsonify({"status": "error", "codigo": 401, "error": "No autenticado"}), 401
    return jsonify({"status": "ok", "usuario": user}), 200

@api_bp.route('/movimientos', methods=['GET'])
def api_movimientos():
    """
    Consulta de movimientos.
    
    PUNTO DE DEMOSTRACIÓN AM01 (SQL INJECTION):
    Si se suministra un filtro manipulado en 'cliente_id' (ej. 1 OR 1=1),
    la consulta concatenada en transfer_repository devolverá las transferencias de todos los usuarios.
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({
            "status": "error",
            "codigo": 401,
            "error": "Debe iniciar sesión para consultar los movimientos."
        }), 401

    results, status, msg = transfer_service.list_movements(user, request.args)
    if results is None:
        return jsonify({"status": "error", "codigo": status, "error": msg}), status

    return jsonify({
        "status": "ok",
        "total": len(results),
        "movimientos": results
    }), 200

@api_bp.route('/transferencias/<id>', methods=['GET'])
def api_detalle_transferencia(id):
    """
    Detalle de transferencia por identificador.
    
    PUNTO DE DEMOSTRACIÓN AM02 (IDOR):
    Verifica sesión activa, pero no comprueba si el usuario es titular ni participa en la transferencia.
    Ana con sesión puede consultar la transferencia ajena 1052 de Bruno.
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({
            "status": "error",
            "codigo": 401,
            "error": "Debe iniciar sesión para ver el detalle de transferencia."
        }), 401

    transfer, status, msg = transfer_service.get_transfer_details(user, id)
    if not transfer:
        return jsonify({"status": "error", "codigo": status, "error": msg}), status

    return jsonify({
        "status": "ok",
        "transferencia": transfer
    }), 200

@api_bp.route('/transferencias', methods=['POST'])
def api_crear_transferencia():
    """
    Procesa una orden de transferencia.
    Coordina con el motor C y responde 501 si el motor aún no está compilado.
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({"status": "error", "codigo": 401, "error": "Sesión requerida."}), 401

    data = request.get_json(silent=True) or request.form
    origen = data.get('cuenta_origen_id')
    destino = data.get('cuenta_destino_id')
    monto = data.get('monto_soles')

    ok, result, status = transfer_service.process_transfer(user, origen, destino, monto)
    return jsonify(result), status
