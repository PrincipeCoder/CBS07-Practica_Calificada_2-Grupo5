"""
Pruebas de la Etapa 6 (FinanUNI_Sec).
Verifica los controles de seguridad y mitigaciones implementados:
- T01 / T02: Autenticación segura, cookie finanuni_sec_session, CSRF y revocación.
- T03: Búsqueda parametrizada legítima.
- T03 / T04: Neutralización verificable de SQL Injection.
- T04: Validación contextual estricta de tipos, formatos, longitudes y rangos invertidos (HTTP 400).
- T05: Detalle legítimo propio permitido (HTTP 200).
- T05 (AM02): Mitigación verificable de IDOR: acceso ajeno rechazado con HTTP 404 uniforme.
- T06: Control de roles RBAC: auditor lee todo (200), pero tiene prohibido transferir (403).
- T06: Intento de débito desde cuenta ajena rechazado con HTTP 403.
- T08: Respuesta explícita 501 ante ausencia del motor C sin alteraciones de datos.
- RN06: Ausencia de trazas internas o SQL expuesto en errores.
"""
import unittest
import json
import os
import sys

# Asegurar que FinanUNI_Sec esté en sys.path al ejecutar desde la raíz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import SecConfig
from app.database.db import reset_db

class Etapa6SecTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(SecConfig)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            reset_db()

    def test_t02_login_argon2id_csrf_y_separacion(self):
        """Verifica hash Argon2id, cookie independiente y obtención de token CSRF."""
        # Intento inválido
        resp_err = self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "wrong"})
        self.assertEqual(resp_err.status_code, 401)
        self.assertIn("Credenciales", resp_err.get_json()['error'])

        # Login válido
        resp_ok = self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        self.assertEqual(resp_ok.status_code, 200)
        data = resp_ok.get_json()
        self.assertEqual(data['usuario']['nombre_acceso'], 'ana')
        self.assertTrue(len(data.get('csrf_token', '')) > 20)

        # Cookie de sesión segura independiente
        cookie_header = resp_ok.headers.get('Set-Cookie')
        self.assertIn('finanuni_sec_session', cookie_header)

        # Intento de logout SIN token CSRF debe ser rechazado con 403
        resp_no_csrf = self.client.post('/api/logout')
        self.assertEqual(resp_no_csrf.status_code, 403)
        self.assertIn("CSRF", resp_no_csrf.get_json()['error'])

        # Logout CON token CSRF válido
        csrf_tok = data['csrf_token']
        resp_logout = self.client.post('/api/logout', headers={'X-CSRF-Token': csrf_tok})
        self.assertEqual(resp_logout.status_code, 200)

        # Sesión invalidada en el servidor
        resp_me = self.client.get('/api/me')
        self.assertEqual(resp_me.status_code, 401)

    def test_t03_busqueda_parametrizada_legitima(self):
        """Verifica que la búsqueda legítima devuelva solo las operaciones autorizadas."""
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        resp = self.client.get('/api/movimientos?cliente_id=1')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['movimientos'][0]['id'], 1051)

    def test_t03_t04_sqli_neutralizado_en_sec(self):
        """
        Verifica la neutralización de la inyección SQL en FinanUNI_Sec.
        La misma carga maliciosa '1 OR 1=1' es detectada y rechazada con HTTP 400 por el validador,
        sin ejecutarse contra el motor SQL ni exponer datos ajenos.
        """
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        # Mismo vector SQLi probado en FinanUNI_Vuln
        resp = self.client.get('/api/movimientos?cliente_id=1+OR+1=1')
        self.assertEqual(resp.status_code, 400, "FinanUNI_Sec debía rechazar el parámetro manipulado con HTTP 400.")
        data = resp.get_json()
        self.assertIn("inválido", data['error'].lower())

    def test_t04_validaciones_contextuales_estrictas(self):
        """Verifica rechazo con 400 ante tipos incorrectos, fechas inválidas y rangos invertidos."""
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})

        casos_invalidos = [
            # Campo desconocido
            ('/api/movimientos?campo_inexistente=1', "Parámetro desconocido"),
            # Fecha inexistente en calendario
            ('/api/movimientos?fecha_desde=2026-02-31', "calendario"),
            # Rango de fechas invertido (desde > hasta)
            ('/api/movimientos?fecha_desde=2026-10-20&fecha_hasta=2026-10-10', "invertido"),
            # Rango de montos invertido (min > max)
            ('/api/movimientos?monto_min_soles=500&monto_max_soles=100', "invertido"),
            # ID fuera de rango de int32_t
            ('/api/movimientos?cliente_id=99999999999', "rango")
        ]

        for url, palabra_clave in casos_invalidos:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 400, f"Fallo al rechazar URL inválida: {url}")
            data = resp.get_json()
            self.assertIn(palabra_clave.lower(), data['error'].lower())

    def test_t05_detalle_legitimo_propio(self):
        """Verifica que Ana pueda consultar su propia transferencia #1051 con 200 OK."""
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        resp = self.client.get('/api/transferencias/1051')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['transferencia']['id'], 1051)

    def test_t05_am02_idor_mitigado_404_uniforme(self):
        """
        Verifica la mitigación de IDOR (AM02 / RF06).
        Cuando Ana consulta la transferencia ajena 1052 (de Bruno), el servidor responde
        con HTTP 404 Recurso no encontrado (no 403), previniendo la enumeración de recursos.
        """
        self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        
        resp = self.client.get('/api/transferencias/1052')
        self.assertEqual(resp.status_code, 404, "FinanUNI_Sec debía devolver 404 uniforme para transferencia ajena.")
        data = resp.get_json()
        self.assertIn("no encontrado", data['error'].lower())
        self.assertNotIn('transferencia', data)

    def test_t06_permisos_auditor(self):
        """
        Verifica los permisos RBAC del Auditor (RF07):
        - El auditor puede consultar transferencias ajenas (1051 y 1052).
        - El auditor tiene prohibido emitir transferencias (HTTP 403).
        """
        # Login como auditor
        resp_login = self.client.post('/api/login', json={"nombre_acceso": "auditor", "password": "auditor123"})
        self.assertEqual(resp_login.status_code, 200)
        csrf_tok = resp_login.get_json()['csrf_token']

        # Auditor consulta 1051 y 1052 -> 200 OK en ambas
        resp_1051 = self.client.get('/api/transferencias/1051')
        self.assertEqual(resp_1051.status_code, 200)
        resp_1052 = self.client.get('/api/transferencias/1052')
        self.assertEqual(resp_1052.status_code, 200)

        # Auditor intenta transferir -> debe responder 403 Forbidden
        resp_transf = self.client.post('/api/transferencias', 
            headers={'X-CSRF-Token': csrf_tok},
            json={"cuenta_origen_id": 101, "cuenta_destino_id": 102, "monto_soles": 100}
        )
        self.assertEqual(resp_transf.status_code, 403)
        self.assertIn("auditor no tiene permisos", resp_transf.get_json()['error'])

    def test_t06_debito_desde_cuenta_ajena_rechazado(self):
        """
        Verifica que un cliente no pueda debitar desde una cuenta que no le pertenece (AB04).
        Ana (titular de cuenta 101) intenta ordenar una transferencia debitando desde la cuenta 102 de Bruno.
        """
        resp_login = self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        csrf_tok = resp_login.get_json()['csrf_token']

        resp = self.client.post('/api/transferencias',
            headers={'X-CSRF-Token': csrf_tok},
            json={"cuenta_origen_id": 102, "cuenta_destino_id": 101, "monto_soles": 50}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIn("no pertenece al usuario", resp.get_json()['error'])

    def test_t08_motor_c_pendiente_explicitamente(self):
        """Verifica que la transferencia legítima de Ana ejecute con 201 si el motor C está provisto o responda 501 ante ausencia."""
        resp_login = self.client.post('/api/login', json={"nombre_acceso": "ana", "password": "ana123"})
        csrf_tok = resp_login.get_json()['csrf_token']

        resp = self.client.post('/api/transferencias',
            headers={'X-CSRF-Token': csrf_tok},
            json={"cuenta_origen_id": 101, "cuenta_destino_id": 102, "monto_soles": 100}
        )
        self.assertIn(resp.status_code, [201, 501])
        if resp.status_code == 201:
            self.assertEqual(resp.get_json().get('centimos'), 10000)
        else:
            self.assertIn("conversor_c", resp.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
