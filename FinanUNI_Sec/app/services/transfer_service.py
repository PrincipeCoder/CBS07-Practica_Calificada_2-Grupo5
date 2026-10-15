"""
Servicio de transferencias (FinanUNI_Sec).
Orquestación segura con validación estricta, RBAC, mitigación de IDOR (404 uniforme)
e integración protegida con el motor C (RN04, RF05, RF06, RF08, RF09).
"""
import os
import json
import subprocess
from app.repositories import transfer_repository, account_repository
from app.security import input_validator, access_control
from app.database.db import get_db_connection

def list_movements(user: dict, raw_filters: dict):
    """
    Consulta transferencias autorizadas para el usuario activo.
    
    ========================================================================================
    CONTROL DE SEGURIDAD (RF05 / RN04 - ALCANCE AUTORIZADO Y PARAMETRIZACIÓN):
    1. Validamos todos los filtros de entrada (tipos, rangos, fechas reales). Si alguno
       contiene datos no permitidos o invertidos, rechazamos con HTTP 400.
    2. Si el usuario es un cliente, delimitamos estrictamente la búsqueda a sus cuentas
       en el servidor (enforced_user_id), impidiendo consultar movimientos de otros clientes.
    3. Si el usuario es auditor, se le permite buscar en todo el sistema.
    ========================================================================================
    """
    if not user:
        return None, 401, "Se requiere sesión activa para consultar movimientos."

    # 1. Validación contextual de filtros
    valid, clean_or_error = input_validator.validate_movement_filters(raw_filters)
    if not valid:
        return None, 400, clean_or_error

    clean = clean_or_error
    is_auditor = (user.get('rol') == 'auditor')
    
    results = transfer_repository.filter_transfers(
        enforced_user_id=user['id'],
        is_auditor=is_auditor,
        target_client_id=clean.get('cliente_id'),
        date_from=clean.get('fecha_desde'),
        date_to=clean.get('fecha_hasta'),
        min_centimos=clean.get('monto_min_centimos'),
        max_centimos=clean.get('monto_max_centimos')
    )
    return results, 200, "OK"

def get_transfer_details(user: dict, raw_transfer_id):
    """
    Obtiene el detalle de una transferencia aplicando control de acceso a nivel de objeto (RF06).
    
    ========================================================================================
    CONTROL DE SEGURIDAD (AM02 / RF06 - MITIGACIÓN DE IDOR Y RESPUESTA 404 UNIFORME):
    1. Validamos que el ID sea un entero positivo válido en [1, 2147483647].
    2. Consultamos la transferencia de forma parametrizada. Si no existe, devolvemos 404.
    3. Autorización por rol y recurso:
       - Auditor: Puede auditar cualquier transferencia (rol 'auditor').
       - Cliente: Debe ser titular de la cuenta origen O de la cuenta destino.
         Si la transferencia pertenece a otro cliente (ej. Ana consultando 1052 de Bruno),
         retornamos HTTP 404 UNIFORME para evitar la enumeración de identificadores ajenos.
    ========================================================================================
    """
    if not user:
        return None, 401, "Se requiere sesión activa."

    # 1. Validar identificador
    valid_id, id_or_error = input_validator.validate_integer_id(raw_transfer_id)
    if not valid_id:
        return None, 400, id_or_error

    transfer_id = id_or_error
    transfer = transfer_repository.find_by_id(transfer_id)
    
    # 2. Si no existe en la base de datos -> 404
    if not transfer:
        return None, 404, "Recurso no encontrado."

    # 3. Comprobación de autorización
    rol = user.get('rol')
    if rol == 'auditor':
        # El rol auditor tiene permiso de lectura global
        return transfer, 200, "OK"

    if rol == 'cliente':
        # El cliente solo puede leer transferencias en las que participa
        if not access_control.check_transfer_participation(user['id'], transfer):
            # Recurso ajeno: retornamos 404 uniforme (no 403) para mitigar enumeración
            return None, 404, "Recurso no encontrado."
        return transfer, 200, "OK"

    # Denegación por defecto ante rol desconocido
    return None, 403, "Acción no permitida al rol."

def resolve_c_engine_binary(motor_dir: str):
    """
    Localiza o compila automáticamente el ejecutable del motor C.
    Busca conversor_c.exe, motor_c.exe, conversor_c, motor_c.
    Si no existe binario pero sí motor_c.c, intenta compilarlo usando MSVC/GCC/Clang.
    """
    if not motor_dir or not os.path.isdir(motor_dir):
        return None

    if os.name == 'nt':
        candidates = ['conversor_c.exe', 'motor_c.exe', 'conversor_c', 'motor_c']
    else:
        candidates = ['conversor_c', 'motor_c', 'conversor_c.exe', 'motor_c.exe']

    for name in candidates:
        candidate_path = os.path.join(motor_dir, name)
        if os.path.isfile(candidate_path) and os.access(candidate_path, os.X_OK | os.R_OK):
            return candidate_path

    # Si no existe ejecutable pero sí motor_c.c, compilar en caliente
    c_source = os.path.join(motor_dir, 'motor_c.c')
    if os.path.isfile(c_source):
        out_bin = "conversor_c.exe" if os.name == 'nt' else "conversor_c"
        out_path = os.path.join(motor_dir, out_bin)

        for compiler in ["gcc", "clang", "cl"]:
            try:
                if compiler in ["gcc", "clang"]:
                    cmd = [compiler, "-O2", "motor_c.c", "-o", out_bin]
                else:
                    cmd = ["cl.exe", f"/Fe:{out_bin}", "motor_c.c"]
                proc = subprocess.run(cmd, cwd=motor_dir, capture_output=True, timeout=10)
                if proc.returncode == 0 and os.path.isfile(out_path):
                    return out_path
            except Exception:
                continue

        if os.name == 'nt':
            vcvars_paths = [
                r"C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
                r"C:\Program Files\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
                r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
            ]
            for vcvars in vcvars_paths:
                if os.path.isfile(vcvars):
                    try:
                        cmd = f'"{vcvars}" && cl.exe /Fe:{out_bin} motor_c.c'
                        proc = subprocess.run(cmd, shell=True, cwd=motor_dir, capture_output=True, timeout=15)
                        if proc.returncode == 0 and os.path.isfile(out_path):
                            return out_path
                    except Exception:
                        continue

    return None

def invoke_c_converter(monto_soles: int):
    """
    Invoca el binario C externo para la conversión monetaria segura (RF08 / AM03).
    Aplica prevalidación de rango en Python antes de invocar a C.
    """
    # 1. Prevalidación básica de tipo y presencia
    if monto_soles is None:
        return False, {"error": "El monto es obligatorio."}, 400

    try:
        soles_val = int(monto_soles)
    except (ValueError, TypeError):
        return False, {"error": "El monto debe ser un entero decimal positivo."}, 400

    if soles_val < 1:
        return False, {"error": "El monto en soles debe ser mayor o igual a 1."}, 400

    # 2. Localizar binario de motor C
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    motor_dir = os.path.join(os.path.dirname(base_dir), "motor_c")
    bin_path = resolve_c_engine_binary(motor_dir)

    if not bin_path:
        alt_motor_dir = os.path.join(base_dir, "motor_c")
        bin_path = resolve_c_engine_binary(alt_motor_dir)

    if not bin_path:
        return False, {
            "error": "El motor numérico en C (conversor_c) aún no ha sido provisto por el Integrante 2.",
            "codigo": 501,
            "dependencia": "motor_c/conversor_c"
        }, 501

    try:
        result = subprocess.run(
            [bin_path, str(soles_val)],
            capture_output=True,
            text=True,
            timeout=2.0,
            shell=False
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            # Verificamos estructura del contrato: {"estado": "OK", "centimos": int}
            if data.get('estado') == 'OK' and 'centimos' in data and isinstance(data['centimos'], int):
                return True, data, 200
            return False, {"error": "Respuesta estructurada inválida del motor C."}, 503
        else:
            data = json.loads(result.stdout.strip()) if result.stdout else {"error": "Fallo en motor C", "codigo_salida": result.returncode}
            return False, data, 422 if "OUT_OF_RANGE" in str(data) else 400
    except subprocess.TimeoutExpired:
        return False, {"error": "Timeout de ejecución en el motor C (límite 2 segundos)."}, 503
    except Exception as e:
        return False, {"error": f"Error del adaptador al motor C: {str(e)}"}, 503

def process_transfer(user: dict, raw_origen_id, raw_destino_id, raw_monto_soles):
    """
    Coordina la secuencia transaccional completa de una transferencia en FinanUNI_Sec (RF09, RF10, RN08).
    """
    if not user:
        return False, {"error": "Se requiere sesión activa.", "codigo": 401}, 401

    # 1. RBAC: El auditor no puede emitir transferencias
    if user.get('rol') != 'cliente':
        return False, {"error": "Acción denegada: el rol auditor no tiene permisos para transferir fondos.", "codigo": 403}, 403

    # 2. Validación de entradas
    ok_o, origen_id = input_validator.validate_integer_id(raw_origen_id)
    if not ok_o:
        return False, {"error": f"Cuenta origen inválida: {origen_id}"}, 400

    ok_d, destino_id = input_validator.validate_integer_id(raw_destino_id)
    if not ok_d:
        return False, {"error": f"Cuenta destino inválida: {destino_id}"}, 400

    if origen_id == destino_id:
        return False, {"error": "La cuenta origen y destino deben ser distintas."}, 400

    ok_m, monto_soles = input_validator.validate_transfer_amount(raw_monto_soles)
    if not ok_m:
        return False, {"error": monto_soles}, 400

    # 3. Comprobación de propiedad (AB04): La cuenta origen debe pertenecer al usuario
    if not access_control.check_account_ownership(user['id'], origen_id):
        return False, {"error": "La cuenta origen no pertenece al usuario autenticado.", "codigo": 403}, 403

    # 4. Comprobar que la cuenta destino existe
    dest_account = account_repository.find_by_id(destino_id)
    if not dest_account:
        return False, {"error": "La cuenta destino no existe.", "codigo": 404}, 404

    # 5. Invocación al motor C
    c_ok, c_result, c_status = invoke_c_converter(monto_soles)
    if not c_ok:
        # El motor aún no está disponible o devolvió rechazo controlado
        return False, c_result, c_status

    centimos = c_result['centimos']

    # 6. Transacción atómica en SQLite (RF10 / RN08)
    conn = get_db_connection()
    try:
        conn.execute("BEGIN TRANSACTION;")
        account_repository.update_balance_atomic(origen_id, -centimos, conn)
        account_repository.update_balance_atomic(destino_id, centimos, conn)
        transfer_id = transfer_repository.create_transfer(origen_id, destino_id, centimos, conn)
        conn.commit()
        return True, {"mensaje": "Transferencia ejecutada exitosamente", "transferencia_id": transfer_id, "centimos": centimos}, 201
    except Exception as e:
        conn.rollback()
        return False, {"error": f"Transacción revertida: {str(e)}"}, 409
