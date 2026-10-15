"""
Pruebas de verificación de infraestructura y rutas del molde inicial para FinanUNI_Sec.
Verifica únicamente:
- Carga de pantallas HTML (HTTP 200).
- Respuesta del endpoint de salud (HTTP 200).
- Respuesta 501 en endpoints de negocio pendientes de implementación.
"""
import unittest
from app import create_app
from app.config import SecConfig

class ScaffoldTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(SecConfig)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_check(self):
        """Verifica que el endpoint /api/health responda 200 con estado operativo en puerto 5001."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertEqual(data.get('app'), 'FinanUNI_Sec')
        self.assertEqual(data.get('port'), 5001)

    def test_pantallas_cargan_exitosamente(self):
        """Verifica que las cuatro pantallas de la interfaz y la de salud carguen con HTTP 200."""
        rutas = ['/login', '/', '/movimientos', '/transferencias/detalle', '/transferencias/nueva', '/health']
        for ruta in rutas:
            response = self.client.get(ruta)
            self.assertEqual(response.status_code, 200, f"Fallo al cargar la ruta {ruta}")

    def test_endpoints_pendientes_responden_501(self):
        """Verifica que todos los endpoints de negocio pendientes retornen HTTP 501."""
        endpoints = [
            ('POST', '/api/login', {}),
            ('POST', '/api/logout', {}),
            ('GET', '/api/movimientos', None),
            ('GET', '/api/transferencias/1051', None),
            ('POST', '/api/transferencias', {"cuenta_origen_id": 101, "cuenta_destino_id": 102, "monto_soles": 100}),
        ]
        for method, endpoint, payload in endpoints:
            if method == 'POST':
                response = self.client.post(endpoint, json=payload or {})
            else:
                response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 501, f"El endpoint {endpoint} no respondió 501")
            data = response.get_json()
            self.assertEqual(data.get('status'), 'pending')
            self.assertIn("pendiente de implementación", data.get('mensaje', ''))

if __name__ == '__main__':
    unittest.main()
