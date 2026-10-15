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

def invoke_c_converter(monto_soles: int):
    """
    Invoca el binario nativo en C según el contrato acordado en conversor.h (RF08).
    
    Comprobamos si el ejecutable 'conversor_c' existe:
    - Si el ejecutable aún no ha sido provisto/compilado por el Integrante 2,
      retornamos estado explícito 501 indicando la dependencia pendiente.
    - No inventamos ni simulamos un cálculo con Python silencioso.
    """
    # Buscamos conversor_c o conversor_c.exe en la carpeta motor_c
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    motor_dir = os.path.join(os.path.dirname(base_dir), "motor_c")
    bin_path = os.path.join(motor_dir, "conversor_c.exe" if os.name == 'nt' else "conversor_c")
    
    if not os.path.exists(bin_path):
        alt_path = os.path.join(base_dir, "motor_c", "conversor_c.exe" if os.name == 'nt' else "conversor_c")
        if os.path.exists(alt_path):
            bin_path = alt_path
        else:
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
            timeout=1.0,
            shell=False
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            return True, data, 200
        else:
            data = json.loads(result.stdout.strip()) if result.stdout else {"motivo": "ERROR_EXIT"}
            return False, data, 400
    except subprocess.TimeoutExpired:
        return False, {"error": "Timeout de ejecución en el motor C (límite 1 segundo)."}, 503
    except Exception as e:
        return False, {"error": f"Error ejecutando conversor_c: {str(e)}"}, 503

def process_transfer(user: dict, cuenta_origen_id: int, cuenta_destino_id: int, monto_soles: int):
    """
    Coordina la transferencia monetaria. Depende de la disponibilidad del motor C.
    """
    if not user:
        return False, {"error": "Se requiere sesión activa.", "codigo": 401}, 401
    
    # Comprobamos la disponibilidad del motor C
    ok, c_result, status = invoke_c_converter(monto_soles)
    if not ok:
        # Retornamos el estado pendiente del motor sin simular transferencias
        return False, c_result, status
    
    # Cuando el motor C esté compilado, se aplicará la transacción atómica
    return True, {"mensaje": "Transferencia procesada"}, 201
