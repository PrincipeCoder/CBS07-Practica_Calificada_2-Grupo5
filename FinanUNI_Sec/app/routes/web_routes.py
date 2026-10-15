"""
Rutas web para servir las pantallas HTML y la navegación de demostración (FinanUNI_Sec).
"""
from flask import Blueprint, render_template, current_app

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
@web_bp.route('/login')
def login():
    """Pantalla 1: Inicio de sesión (Demo de acceso ficticio)."""
    return render_template('login.html', active_page='login')

@web_bp.route('/movimientos')
def movimientos():
    """Pantalla 2: Consulta de movimientos con filtros y datos estáticos de muestra."""
    # Datos de muestra estáticos para visualización de maquetación (NO proceden de consultas)
    sample_movements = [
        {
            "id": 1051,
            "origen": 101,
            "destino": 102,
            "monto_soles": "100.00",
            "monto_centimos": 10000,
            "fecha": "2026-10-14 10:00:00 UTC",
            "descripcion": "Transferencia de Ana a Bruno"
        },
        {
            "id": 1052,
            "origen": 102,
            "destino": 103,
            "monto_soles": "200.00",
            "monto_centimos": 20000,
            "fecha": "2026-10-14 11:30:00 UTC",
            "descripcion": "Transferencia entre cuentas de Bruno"
        },
        {
            "id": 1053,
            "origen": 103,
            "destino": 102,
            "monto_soles": "50.00",
            "monto_centimos": 5000,
            "fecha": "2026-10-14 12:15:00 UTC",
            "descripcion": "Retorno de fondos cuenta secundaria"
        }
    ]
    return render_template('movimientos.html', active_page='movimientos', sample_data=sample_movements)

@web_bp.route('/transferencias/detalle')
def detalle_transferencia():
    """Pantalla 3: Detalle de transferencia con buscador y datos estáticos de muestra."""
    sample_detail = {
        "id": 1051,
        "cuenta_origen": 101,
        "titular_origen": "Ana (Cliente)",
        "cuenta_destino": 102,
        "titular_destino": "Bruno (Cliente)",
        "monto_soles": "100.00",
        "monto_centimos": 10000,
        "fecha_utc": "2026-10-14 10:00:00 UTC",
        "estado": "CONFIRMADA (Histórico de muestra)",
        "correlacion_id": "00000000-0000-0000-0000-000000000001"
    }
    return render_template('detalle_transferencia.html', active_page='detalle', sample_data=sample_detail)

@web_bp.route('/transferencias/nueva')
def nueva_transferencia():
    """Pantalla 4: Formulario para ordenar una nueva transferencia monetaria."""
    return render_template('nueva_transferencia.html', active_page='nueva_transferencia')

@web_bp.route('/health')
def health_page():
    """Pantalla informativa del estado de salud e infraestructura de la aplicación."""
    return render_template('health.html', active_page='health')
