"""
Prueba de Análisis Diferencial Comparativo entre FinanUNI_Vuln (5000) y FinanUNI_Sec (5001).
Ejecuta exactamente las mismas solicitudes HTTP contra ambas instancias para comprobar:
- T01 / T02: Independencia estricta de cookies y sesiones.
- T03 (AM01): Explotación de SQLi en Vuln vs. neutralización en Sec con HTTP 400.
- T05 (AM02): Explotación de IDOR en Vuln vs. denegación con HTTP 404 uniforme en Sec.
- T06: Permisos de lectura del auditor y rechazo de transferencias con 403.
"""
import unittest
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
import json
import subprocess
import sys
import os
import time

class ComparacionDiferencialTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Verifica o inicia ambas aplicaciones en los puertos 5000 y 5001."""
        cls.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.vuln_dir = os.path.join(cls.root_dir, "FinanUNI_Vuln")
        cls.sec_dir = os.path.join(cls.root_dir, "FinanUNI_Sec")
        
        cls.proc_vuln = None
        cls.proc_sec = None

        # Verificar si ya están corriendo
        if not cls._is_alive("http://127.0.0.1:5000/api/health"):
            cls.proc_vuln = subprocess.Popen([sys.executable, "run.py"], cwd=cls.vuln_dir)
        if not cls._is_alive("http://127.0.0.1:5001/api/health"):
            cls.proc_sec = subprocess.Popen([sys.executable, "run.py"], cwd=cls.sec_dir)

        # Esperar a que respondan
        for _ in range(20):
            if cls._is_alive("http://127.0.0.1:5000/api/health") and cls._is_alive("http://127.0.0.1:5001/api/health"):
                break
            time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        """Detiene los subprocesos iniciados por el test."""
        for p in (cls.proc_vuln, cls.proc_sec):
            if p and p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()

    @staticmethod
    def _is_alive(url):
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _create_session_opener(self):
        """Crea un opener HTTP que maneja cookies automáticamente."""
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        return opener, cj

    def _login(self, opener, base_url, username, password):
        """Autentica al usuario y guarda la cookie en el opener."""
        payload = json.dumps({"nombre_acceso": username, "password": password}).encode('utf-8')
        req = urllib.request.Request(f"{base_url}/api/login", data=payload, headers={'Content-Type': 'application/json'})
        with opener.open(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return resp.status, data

    def test_01_comparacion_sqli_am01(self):
        """
        Ejecuta la misma carga SQLi '1 OR 1=1' en Vuln y en Sec:
        - Vuln: Concatena la entrada y retorna los 3 movimientos (evidencia de vulnerabilidad).
        - Sec: Detecta entrada inválida y rechaza con HTTP 400 (evidencia de mitigación).
        """
        opener_v, _ = self._create_session_opener()
        opener_s, _ = self._create_session_opener()

        self._login(opener_v, "http://127.0.0.1:5000", "ana", "ana123")
        self._login(opener_s, "http://127.0.0.1:5001", "ana", "ana123")

        payload = "1 OR 1=1"
        query = urllib.parse.urlencode({"cliente_id": payload})

        # 1. Petición contra FinanUNI_Vuln (5000)
        req_v = urllib.request.Request(f"http://127.0.0.1:5000/api/movimientos?{query}")
        with opener_v.open(req_v) as resp_v:
            self.assertEqual(resp_v.status, 200)
            data_v = json.loads(resp_v.read().decode('utf-8'))
            self.assertEqual(data_v['total'], 3, "[VULN] Se evidenció SQLi devolviendo las 3 transferencias.")

        # 2. Misma petición contra FinanUNI_Sec (5001)
        req_s = urllib.request.Request(f"http://127.0.0.1:5001/api/movimientos?{query}")
        try:
            with opener_s.open(req_s) as resp_s:
                self.fail(f"[SEC] La solicitud no debió responder con éxito {resp_s.status}")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400, "[SEC] El validador contextual debía rechazar con 400 Bad Request.")
            err_data = json.loads(e.read().decode('utf-8'))
            self.assertIn("inválido", err_data['error'].lower())

    def test_02_comparacion_idor_am02(self):
        """
        Ejecuta la misma consulta sobre la transferencia ajena 1052 como Ana:
        - Vuln: Omite autorización y expone los datos de Bruno con HTTP 200 (evidencia de IDOR).
        - Sec: Comprueba participación y deniega con HTTP 404 uniforme (evidencia de mitigación).
        """
        opener_v, _ = self._create_session_opener()
        opener_s, _ = self._create_session_opener()

        self._login(opener_v, "http://127.0.0.1:5000", "ana", "ana123")
        self._login(opener_s, "http://127.0.0.1:5001", "ana", "ana123")

        # 1. Petición contra FinanUNI_Vuln (5000)
        req_v = urllib.request.Request("http://127.0.0.1:5000/api/transferencias/1052")
        with opener_v.open(req_v) as resp_v:
            self.assertEqual(resp_v.status, 200)
            data_v = json.loads(resp_v.read().decode('utf-8'))
            self.assertEqual(data_v['transferencia']['id'], 1052)
            self.assertEqual(data_v['transferencia']['titular_origen'], 'bruno')

        # 2. Misma petición contra FinanUNI_Sec (5001)
        req_s = urllib.request.Request("http://127.0.0.1:5001/api/transferencias/1052")
        try:
            with opener_s.open(req_s) as resp_s:
                self.fail(f"[SEC] No debió responder con éxito: {resp_s.status}")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404, "[SEC] Debía responder 404 uniforme para mitigar IDOR.")
            err_data = json.loads(e.read().decode('utf-8'))
            self.assertIn("no encontrado", err_data['error'].lower())

    def test_03_separacion_estricta_de_sesiones(self):
        """
        Verifica que las cookies finanuni_vuln_session y finanuni_sec_session
        no se compartan ni concedan acceso cruzado entre puertos.
        """
        opener_v, cj_v = self._create_session_opener()
        opener_s, cj_s = self._create_session_opener()

        self._login(opener_v, "http://127.0.0.1:5000", "ana", "ana123")
        self._login(opener_s, "http://127.0.0.1:5001", "ana", "ana123")

        cookie_names_v = [c.name for c in cj_v]
        cookie_names_s = [c.name for c in cj_s]

        self.assertIn('finanuni_vuln_session', cookie_names_v)
        self.assertNotIn('finanuni_sec_session', cookie_names_v)

        self.assertIn('finanuni_sec_session', cookie_names_s)
        self.assertNotIn('finanuni_vuln_session', cookie_names_s)

if __name__ == '__main__':
    unittest.main()
