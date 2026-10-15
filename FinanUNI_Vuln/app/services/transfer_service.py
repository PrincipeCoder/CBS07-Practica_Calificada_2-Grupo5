"""
Servicio de transferencias (FinanUNI_Vuln).
Contiene la orquestación de movimientos, detalle y transferencias.
Incluye las vulnerabilidades deliberadas de SQLi (en búsqueda) e IDOR (en detalle)
debidamente aisladas y comentadas con fines académicos.
"""
import os
import json
import subprocess
from app.repositories import transfer_repository, account_repository
from app.database.db import get_db_connection

def list_movements(user: dict, filters: dict):
    """
    Consulta transferencias filtradas en FinanUNI_Vuln.
    
    Comprobamos si el usuario tiene sesión activa:
    - En esta versión vulnerable, pasamos directamente el parámetro 'cliente_id' enviado en los filtros
      al repositorio, permitiendo la demostración de SQL Injection concatenada (AM01 / CWE-89).
    """
    if not user:
        return None, 401, "Se requiere iniciar sesión para consultar movimientos."
    
    cliente_id = filters.get('cliente_id')
    date_from = filters.get('fecha_desde')
    date_to = filters.get('fecha_hasta')
    
    min_centimos = None
    if filters.get('monto_min_soles'):
        try:
            min_centimos = int(filters['monto_min_soles']) * 100
        except ValueError:
            pass
            
    max_centimos = None
    if filters.get('monto_max_soles'):
        try:
            max_centimos = int(filters['monto_max_soles']) * 100
        except ValueError:
            pass

    try:
        results = transfer_repository.filter_transfers(
            client_id=cliente_id,
            date_from=date_from,
            date_to=date_to,
            min_centimos=min_centimos,
            max_centimos=max_centimos
        )
        return results, 200, "OK"
    except Exception as e:
        # En la versión vulnerable SQLite puede lanzar OperationalError ante sintaxis inyectada rota
        return None, 500, f"Error en consulta SQL: {str(e)}"

def get_transfer_details(user: dict, transfer_id: int):
    """
    Obtiene los detalles de una transferencia por su identificador.
    
    ========================================================================================
    DEFECTO DELIBERADO (VULNERABILIDAD ACADÉMICA AM02 / CWE-639 - IDOR):
    Comprobamos que el usuario esté autenticado en el sistema (user no es None),
    pero OMITIMOS deliberadamente comprobar si el usuario es titular de la cuenta origen
    o destino de la transferencia.
    
    Consecuencia observable: Ana (usuario 1) puede consultar la transferencia 1052
    (operación privada entre las cuentas 102 y 103 de Bruno) con solo manipular el ID en la URL.
    ========================================================================================
    """
    if not user:
        return None, 401, "Se requiere sesión activa."
    
    try:
        t_id = int(transfer_id)
    except (ValueError, TypeError):
        return None, 400, "Identificador de transferencia inválido."
    
    transfer = transfer_repository.find_by_id(t_id)
    if not transfer:
        return None, 404, "Transferencia no encontrada."
    
    # PUNTO VULNERABLE: Se retorna el registro sin validar propiedad ni rol
    return transfer, 200, "OK"

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
    Invoca el binario nativo en C según el contrato acordado en conversor.h (RF08).
    En FinanUNI_Vuln ejecuta el motor C vulnerable que sobrepasa INT32_MAX sin control.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    motor_dir = os.path.join(os.path.dirname(base_dir), "motor_c")
    bin_path = resolve_c_engine_binary(motor_dir)

    if not bin_path:
        alt_motor_dir = os.path.join(base_dir, "motor_c")
        bin_path = resolve_c_engine_binary(alt_motor_dir)

    if not bin_path:
        return False, {
            "error": "El motor numérico en C (conversor_c) aún no ha sido compilado por el Integrante 2.",
            "codigo": 501,
            "dependencia": "motor_c/conversor_c"
        }, 501

    try:
        result = subprocess.run(
            [bin_path, str(monto_soles)],
            capture_output=True,
            text=True,
            timeout=2.0,
            shell=False
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            return True, data, 200
        else:
            data = json.loads(result.stdout.strip()) if result.stdout else {"motivo": "ERROR_EXIT", "codigo_salida": result.returncode}
            return False, data, 400
    except subprocess.TimeoutExpired:
        return False, {"error": "Timeout de ejecución en el motor C (límite 2 segundos)."}, 503
    except Exception as e:
        return False, {"error": f"Error ejecutando conversor_c: {str(e)}"}, 503

def process_transfer(user: dict, cuenta_origen_id, cuenta_destino_id, monto_soles):
    """
    Coordina la transferencia monetaria en FinanUNI_Vuln.
    - Ausencia deliberada de validación estricta de propiedad y rango numérico (AM03).
    - Aplica la conversión del motor C vulnerable y persiste el resultado en SQLite.
    """
    if not user:
        return False, {"error": "Se requiere sesión activa.", "codigo": 401}, 401
    
    try:
        origen_id = int(cuenta_origen_id)
        destino_id = int(cuenta_destino_id)
        monto_s = int(monto_soles)
    except (ValueError, TypeError):
        return False, {"error": "Identificadores de cuenta y monto deben ser números enteros."}, 400

    if origen_id == destino_id:
        return False, {"error": "La cuenta origen y destino deben ser distintas."}, 400

    # Comprobamos la disponibilidad del motor C
    ok, c_result, status = invoke_c_converter(monto_s)
    if not ok:
        return False, c_result, status
    
    centimos = c_result.get('centimos', 0)

    # Conexión directa a base de datos SQLite (FinanUNI_Vuln)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE cuentas SET saldo_centimos = saldo_centimos - ? WHERE id = ?;", (centimos, origen_id))
        cursor.execute("UPDATE cuentas SET saldo_centimos = saldo_centimos + ? WHERE id = ?;", (centimos, destino_id))
        transfer_id = transfer_repository.create_transfer(origen_id, destino_id, centimos, conn)
        conn.commit()
        return True, {
            "mensaje": "Transferencia ejecutada en FinanUNI_Vuln",
            "transferencia_id": transfer_id,
            "centimos": centimos
        }, 201
    except Exception as e:
        conn.rollback()
        return False, {"error": f"Error en BD: {str(e)}"}, 500
