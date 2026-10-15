"""
Pruebas de la Etapa 5 (FinanUNI_Vuln).
Verifica:
- T01 / T02: Autenticación, revocación de sesión y persistencia.
- T03: Búsqueda legítima de movimientos.
- T03 (AM01): Reproducción verificable de SQL Injection mediante alteración de lógica booleana.
- T05: Detalle legítimo de transferencia propia.
- T05 (AM02): Reproducción verificable de IDOR consultando transferencia 1052 ajena.
- T08: Respuesta explícita 501 ante ausencia del motor C.
"""
import unittest
import os
import sys

# Asegurar que FinanUNI_Vuln esté en sys.path al ejecutar desde la raíz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import VulnConfig
from app.database.db import reset_db

class Etapa5VulnTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(VulnConfig)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            reset_db()

    def test_t02_login_valido_e_invalido(self):
        """Verifica autenticación funcional con Argon2id y rechazo con credenciales erróneas."""
        # Intento con contraseña errónea
        resp_err = self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "wrongpassword"})
        self.assertEqual(resp_err.status_code, 401)
        self.assertIn("Credenciales", resp_err.get_json()['error'])

        # Login válido con Ana
        resp_ok = self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        self.assertEqual(resp_ok.status_code, 200)
        self.assertEqual(resp_ok.get_json()['usuario']['nombre_acceso'], 'ana')
        
        # Comprobar que se emite la cookie finanuni_vuln_session
        cookie_header = resp_ok.headers.get('Set-Cookie')
        self.assertIn('finanuni_vuln_session', cookie_header)

        # Logout revoca la sesión
        resp_logout = self.client.post('/api/logout')
        self.assertEqual(resp_logout.status_code, 200)

        # Solicitud protegida tras logout debe retornar 401
        resp_me = self.client.get('/api/me')
        self.assertEqual(resp_me.status_code, 401)

    def test_t03_busqueda_legitima_movimientos(self):
        """Verifica que un filtro legítimo retorne únicamente las transferencias de Ana."""
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        # Filtro legítimo por cliente 1 (Ana)
        resp = self.client.get('/api/movimientos?cliente_id=1')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['movimientos'][0]['id'], 1051)

    def test_t03_am01_sqli_reproducible_vuln(self):
        """
        Confirma la vulnerabilidad AM01 (SQL Injection) en FinanUNI_Vuln.
        Al inyectar '1 OR 1=1' en la consulta concatenada, se recuperan transferencias de todos los clientes.
        """
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        # Vector SQL Injection en el parámetro cliente_id
        payload_sqli = "1 OR 1=1"
        resp = self.client.get(f'/api/movimientos?cliente_id={payload_sqli}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        
        # En la semilla acordada hay 3 transferencias: 1051, 1052 y 1053.
        # La inyección debe devolver las 3 operaciones demostrando la alteración de la cláusula WHERE.
        self.assertEqual(data['total'], 3, "La inyección SQL debía alterar la selección devolviendo 3 registros.")
        ids = [m['id'] for m in data['movimientos']]
        self.assertIn(1051, ids)
        self.assertIn(1052, ids)
        self.assertIn(1053, ids)

    def test_t05_detalle_legitimo_ana(self):
        """Verifica que Ana pueda consultar su propia transferencia legítima #1051."""
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        resp = self.client.get('/api/transferencias/1051')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['transferencia']['id'], 1051)
        self.assertEqual(data['transferencia']['cuenta_origen_id'], 101)

    def test_t05_am02_idor_reproducible_vuln(self):
        """
        Confirma la vulnerabilidad AM02 (IDOR) en FinanUNI_Vuln.
        Ana consulta la transferencia #1052 (entre cuentas 102 y 103 de Bruno)
        y la API se la expone sin verificar autorización sobre el recurso.
        """
        # Ana inicia sesión
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        # Ana solicita la transferencia ajena 1052
        resp = self.client.get('/api/transferencias/1052')
        self.assertEqual(resp.status_code, 200, "FinanUNI_Vuln debía exponer 1052 debido a la omisión de autorización.")
        data = resp.get_json()
        self.assertEqual(data['transferencia']['id'], 1052)
        self.assertEqual(data['transferencia']['titular_origen'], 'bruno')
        self.assertEqual(data['transferencia']['titular_destino'], 'bruno')

    def test_t08_motor_c_pendiente_explicitamente(self):
        """Verifica que la transferencia responda 501 sin alterar saldos ante ausencia del binario C."""
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        resp = self.client.post('/api/transferencias', json={
            "cuenta_origen_id": 101,
            "cuenta_destino_id": 102,
            "monto_soles": 100
        })
        self.assertEqual(resp.status_code, 501)
        self.assertIn("conversor_c", resp.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
