"""
Rutas de API REST de FinanUNI_Sec (Puerto 5001).
Implementa endpoints protegidos con parametrización estricta, validación contextual,
mitigación de IDOR (404 uniforme), RBAC y protección CSRF (RN04, RN05, RN06, RF05, RF06, RF07).
"""
from flask import Blueprint, jsonify, request, current_app, make_response
from app.services import auth_service, transfer_service
from app.security import csrf

api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_authenticated_user():
    """
    Carga de forma confiable la identidad y rol del usuario desde la base de datos del servidor.
    Nunca confía en encabezados de rol ni campos de usuario enviados por el cliente.
    """
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'finanuni_sec_session')
    session_token = request.cookies.get(cookie_name)
    if not session_token:
        return None
    return auth_service.validate_active_session(session_token)

def verify_csrf(session_id: str):
    """
    Verifica la presencia y validez del token CSRF en solicitudes mutables (AM08).
    """
    token_received = request.headers.get('X-CSRF-Token')
    if not token_received:
        data = request.get_json(silent=True) or request.form
        token_received = data.get('csrf_token') if data else None

    return csrf.validate_csrf_token(session_id, token_received)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servidor."""
    return jsonify({
        "status": "ok",
        "app": current_app.config.get('APP_NAME'),
        "port": current_app.config.get('PORT'),
        "is_vulnerable_app": False,
        "stage": "etapa_6",
        "message": "Servidor seguro activo. Controles de parametrización, RBAC y CSRF operativos."
    }), 200

@api_bp.route('/login', methods=['POST'])
def api_login():
    """
    Autenticación segura con Argon2id y asignación de token CSRF.
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

    csrf_token = csrf.generate_csrf_token(token_or_err)
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'finanuni_sec_session')
    
    response = make_response(jsonify({
        "status": "ok",
        "mensaje": "Inicio de sesión seguro exitoso.",
        "usuario": {
            "id": user['id'],
            "nombre_acceso": user['nombre_acceso'],
            "rol": user['rol']
        },
        "csrf_token": csrf_token
    }), 200)

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
    Cierre de sesión seguro con comprobación de token CSRF (RN05 / AM08).
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({"status": "error", "codigo": 401, "error": "Sesión no activa."}), 401

    if not verify_csrf(user['session_id']):
        return jsonify({"status": "error", "codigo": 403, "error": "Token CSRF inválido o ausente."}), 403

    auth_service.logout_session(user['session_id'])
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'finanuni_sec_session')
    
    response = make_response(jsonify({
        "status": "ok",
        "mensaje": "Sesión revocada e invalidada en el servidor."
    }), 200)
    response.delete_cookie(cookie_name)
    return response

@api_bp.route('/me', methods=['GET'])
def api_me():
    """Retorna los datos del usuario activo y su token CSRF."""
    user = get_authenticated_user()
    if not user:
        return jsonify({"status": "error", "codigo": 401, "error": "No autenticado"}), 401
    
    csrf_token = csrf.generate_csrf_token(user['session_id'])
    return jsonify({
        "status": "ok",
        "usuario": user,
        "csrf_token": csrf_token
    }), 200

@api_bp.route('/movimientos', methods=['GET'])
def api_movimientos():
    """
    Consulta de movimientos segura (RF05).
    Valida parámetros estrictamente y aplica alcance en el servidor.
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({
            "status": "error",
            "codigo": 401,
            "error": "Debe iniciar sesión para consultar movimientos."
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
    Detalle de transferencia protegido contra IDOR (RF06 / AM02).
    Si el recurso no existe o pertenece a otro cliente, devuelve 404 UNIFORME.
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({
            "status": "error",
            "codigo": 401,
            "error": "Se requiere sesión activa."
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
    Creación de transferencias con RBAC, verificación de titularidad y token CSRF.
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({"status": "error", "codigo": 401, "error": "Sesión requerida."}), 401

    # Comprobación obligatoria de token CSRF para escrituras
    if not verify_csrf(user['session_id']):
        return jsonify({"status": "error", "codigo": 403, "error": "Token CSRF inválido o ausente."}), 403

    data = request.get_json(silent=True) or request.form
    origen = data.get('cuenta_origen_id')
    destino = data.get('cuenta_destino_id')
    monto = data.get('monto_soles')

    ok, result, status = transfer_service.process_transfer(user, origen, destino, monto)
    return jsonify(result), status

# Manejadores de error estandarizados sin filtración de trazas ni SQL (RN06)
@api_bp.app_errorhandler(400)
def handle_400(e):
    return jsonify({"status": "error", "codigo": 400, "error": "Formato de solicitud inválido."}), 400

@api_bp.app_errorhandler(401)
def handle_401(e):
    return jsonify({"status": "error", "codigo": 401, "error": "Identidad no válida o sesión ausente."}), 401

@api_bp.app_errorhandler(403)
def handle_403(e):
    return jsonify({"status": "error", "codigo": 403, "error": "Acción no permitida."}), 403

@api_bp.app_errorhandler(404)
def handle_404(e):
    return jsonify({"status": "error", "codigo": 404, "error": "Recurso no encontrado."}), 404

@api_bp.app_errorhandler(500)
def handle_500(e):
    return jsonify({"status": "error", "codigo": 500, "error": "Error interno controlado del servidor."}), 500
