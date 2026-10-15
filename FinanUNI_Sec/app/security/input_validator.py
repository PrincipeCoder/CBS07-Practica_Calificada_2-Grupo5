"""
Módulo de validación de entradas de servidor (FinanUNI_Sec).
Implementa validación contextual estricta de tipos, rangos, longitudes y formatos (RF05 / T04).
"""
import re
from datetime import datetime

MAX_INT32 = 2147483647
MAX_SOLES = 21474836  # floor(2147483647 / 100)

def validate_integer_id(raw_value):
    """
    Valida que el identificador sea un entero decimal positivo hasta 2147483647 (máx 10 dígitos).
    Rechaza booleanos, estructuras complejas, números negativos o conversiones ambiguas.
    
    :return: (True, int_value) o (False, mensaje_error)
    """
    if raw_value is None or isinstance(raw_value, bool):
        return False, "Identificador ausente o tipo booleano no permitido."
    
    val_str = str(raw_value).strip()
    if not re.fullmatch(r'^[0-9]{1,10}$', val_str):
        return False, "El identificador excede la longitud o rango permitido (debe ser de 1 a 10 dígitos decimales)."
    
    num = int(val_str)
    if num < 1 or num > MAX_INT32:
        return False, f"El identificador debe estar en el rango [1, {MAX_INT32}]."
    
    return True, num

def validate_transfer_amount(raw_amount):
    """
    Valida que el monto de transferencia en soles sea un entero entre 1 y 21474836.
    Rechaza punto decimal, coma, exponentes, signo negativo o float.
    
    :return: (True, int_soles) o (False, mensaje_error)
    """
    if raw_amount is None or isinstance(raw_amount, bool):
        return False, "El monto es obligatorio."
    
    val_str = str(raw_amount).strip()
    # Rechazamos cualquier carácter que no sea un dígito decimal simple (sin punto, coma ni signo)
    if not re.fullmatch(r'^[0-9]+$', val_str):
        return False, "El monto debe ser un entero positivo en soles sin punto decimal ni exponentes."
    
    num = int(val_str)
    if num < 1 or num > MAX_SOLES:
        return False, f"El monto en soles debe situarse entre 1 y {MAX_SOLES} soles enteros."
    
    return True, num

def validate_date_string(raw_date: str):
    """
    Valida que la fecha tenga formato YYYY-MM-DD, 10 caracteres y corresponda a una fecha calendario real.
    
    :return: (True, date_str) o (False, mensaje_error)
    """
    if not raw_date or not isinstance(raw_date, str):
        return False, "Fecha inválida o ausente."
    
    val_str = raw_date.strip()
    if len(val_str) != 10 or not re.fullmatch(r'^\d{4}-\d{2}-\d{2}$', val_str):
        return False, "La fecha debe tener el formato estricto YYYY-MM-DD (10 caracteres)."
    
    try:
        datetime.strptime(val_str, '%Y-%m-%d')
    except ValueError:
        return False, "La fecha proporcionada no corresponde a un día real del calendario."
    
    return True, val_str

def validate_movement_filters(raw_filters: dict):
    """
    Valida y sanea el conjunto de filtros para la consulta de movimientos (RF05 / T04).
    
    Comprueba:
    1. Parámetros desconocidos: rechaza si hay campos no contemplados en el contrato.
    2. cliente_id: si existe, debe ser entero [1, 2147483647].
    3. Fechas: verifica formato ISO y coherencia temporal (desde <= hasta).
    4. Montos: verifica rango entero [0, 21474836] y coherencia de rango (min <= max).
    
    :return: (True, clean_filters) o (False, mensaje_error)
    """
    allowed_keys = {'cliente_id', 'fecha_desde', 'fecha_hasta', 'monto_min_soles', 'monto_max_soles'}
    for key in raw_filters.keys():
        if key not in allowed_keys:
            return False, f"Parámetro desconocido no permitido: '{key}'."
    
    clean = {}

    # 1. cliente_id
    if 'cliente_id' in raw_filters and raw_filters['cliente_id'] != '':
        ok, val = validate_integer_id(raw_filters['cliente_id'])
        if not ok:
            return False, f"Filtro cliente_id inválido: {val}"
        clean['cliente_id'] = val

    # 2. Fechas
    date_from = raw_filters.get('fecha_desde')
    if date_from:
        ok, val = validate_date_string(date_from)
        if not ok:
            return False, f"Filtro fecha_desde inválido: {val}"
        clean['fecha_desde'] = val

    date_to = raw_filters.get('fecha_hasta')
    if date_to:
        ok, val = validate_date_string(date_to)
        if not ok:
            return False, f"Filtro fecha_hasta inválido: {val}"
        clean['fecha_hasta'] = val

    if clean.get('fecha_desde') and clean.get('fecha_hasta'):
        if clean['fecha_desde'] > clean['fecha_hasta']:
            return False, "Rango de fechas invertido: 'fecha_desde' no puede ser posterior a 'fecha_hasta'."

    # 3. Montos en soles
    min_soles = raw_filters.get('monto_min_soles')
    if min_soles is not None and str(min_soles).strip() != '':
        val_str = str(min_soles).strip()
        if not re.fullmatch(r'^[0-9]+$', val_str):
            return False, "monto_min_soles debe ser un entero positivo sin decimales."
        n_min = int(val_str)
        if n_min < 0 or n_min > MAX_SOLES:
            return False, f"monto_min_soles debe estar entre 0 y {MAX_SOLES}."
        clean['monto_min_centimos'] = n_min * 100

    max_soles = raw_filters.get('monto_max_soles')
    if max_soles is not None and str(max_soles).strip() != '':
        val_str = str(max_soles).strip()
        if not re.fullmatch(r'^[0-9]+$', val_str):
            return False, "monto_max_soles debe ser un entero positivo sin decimales."
        n_max = int(val_str)
        if n_max < 0 or n_max > MAX_SOLES:
            return False, f"monto_max_soles debe estar entre 0 y {MAX_SOLES}."
        clean['monto_max_centimos'] = n_max * 100

    if 'monto_min_centimos' in clean and 'monto_max_centimos' in clean:
        if clean['monto_min_centimos'] > clean['monto_max_centimos']:
            return False, "Rango de montos invertido: el monto mínimo no puede exceder al máximo."

    return True, clean
