"""
Script de verificación en vivo del molde inicial:
Comprueba que ambas aplicaciones funcionen simultáneamente en los puertos 5000 y 5001,
que todas las pantallas carguen (HTTP 200) y que los endpoints de negocio respondan HTTP 501.
"""
import urllib.request
import urllib.error
import json
import sys

def check_url(url, expected_code=200):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            body = resp.read().decode('utf-8')
            assert status == expected_code, f"Esperaba {expected_code}, obtuve {status} en {url}"
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        assert e.code == expected_code, f"Esperaba {expected_code}, obtuve {e.code} en {url}"
        return e.code, body

def check_post_501(url, payload):
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as resp:
            raise AssertionError(f"Esperaba 501 en {url}, pero respondió {resp.getcode()} exitoso")
    except urllib.error.HTTPError as e:
        assert e.code == 501, f"Esperaba 501, pero obtuve {e.code} en {url}"
        resp_data = json.loads(e.read().decode('utf-8'))
        assert resp_data.get('status') == 'pending'
        assert "pendiente de implementación" in resp_data.get('mensaje', '')
        return e.code, resp_data

def main():
    print("[*] Iniciando verificación en vivo de FinanUNI_Vuln (5000) y FinanUNI_Sec (5001)...")

    # 1. Comprobar FinanUNI_Vuln (Puerto 5000)
    print("\n--- Verificando FinanUNI_Vuln (Puerto 5000) ---")
    status, body = check_url("http://127.0.0.1:5000/api/health", 200)
    health_vuln = json.loads(body)
    assert health_vuln.get('app') == 'FinanUNI_Vuln'
    print("[+] /api/health respondio 200 OK:", health_vuln)

    for path in ['/', '/login', '/movimientos', '/transferencias/detalle', '/transferencias/nueva', '/health']:
        status, _ = check_url(f"http://127.0.0.1:5000{path}", 200)
        print(f"[+] Pantalla http://127.0.0.1:5000{path} cargo con HTTP 200")

    check_post_501("http://127.0.0.1:5000/api/login", {"nombre_acceso": "ana", "password": "123"})
    print("[+] POST /api/login respondio HTTP 501 (Sin crear sesion)")

    check_url("http://127.0.0.1:5000/api/movimientos", 501)
    print("[+] GET /api/movimientos respondio HTTP 501 (Sin consulta)")

    check_url("http://127.0.0.1:5000/api/transferencias/1051", 501)
    print("[+] GET /api/transferencias/1051 respondio HTTP 501 (Sin consulta)")

    check_post_501("http://127.0.0.1:5000/api/transferencias", {"cuenta_origen_id": 101, "cuenta_destino_id": 102, "monto_soles": 100})
    print("[+] POST /api/transferencias respondio HTTP 501 (Sin transferencia ni cambio de saldos)")

    # 2. Comprobar FinanUNI_Sec (Puerto 5001)
    print("\n--- Verificando FinanUNI_Sec (Puerto 5001) ---")
    status, body = check_url("http://127.0.0.1:5001/api/health", 200)
    health_sec = json.loads(body)
    assert health_sec.get('app') == 'FinanUNI_Sec'
    print("[+] /api/health respondio 200 OK:", health_sec)

    for path in ['/', '/login', '/movimientos', '/transferencias/detalle', '/transferencias/nueva', '/health']:
        status, _ = check_url(f"http://127.0.0.1:5001{path}", 200)
        print(f"[+] Pantalla http://127.0.0.1:5001{path} cargo con HTTP 200")

    check_post_501("http://127.0.0.1:5001/api/login", {"nombre_acceso": "ana", "password": "123"})
    print("[+] POST /api/login respondio HTTP 501 (Sin crear sesion)")

    check_url("http://127.0.0.1:5001/api/movimientos", 501)
    print("[+] GET /api/movimientos respondio HTTP 501 (Sin consulta)")

    check_url("http://127.0.0.1:5001/api/transferencias/1051", 501)
    print("[+] GET /api/transferencias/1051 respondio HTTP 501 (Sin consulta)")

    check_post_501("http://127.0.0.1:5001/api/transferencias", {"cuenta_origen_id": 101, "cuenta_destino_id": 102, "monto_soles": 100})
    print("[+] POST /api/transferencias respondio HTTP 501 (Sin transferencia ni cambio de saldos)")

    print("\n[EXITO] VERIFICACION TOTALMENTE EXITOSA: Ambas aplicaciones operan en simultaneo y respetan los contratos.")

if __name__ == '__main__':
    main()
