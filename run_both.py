"""
Script utilitario para arrancar simultáneamente FinanUNI_Vuln (5000) y FinanUNI_Sec (5001).
Uso:
    python run_both.py
"""
import sys
import subprocess
import os
import signal
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    vuln_dir = os.path.join(root_dir, "FinanUNI_Vuln")
    sec_dir = os.path.join(root_dir, "FinanUNI_Sec")

    python_exec = sys.executable

    print("=================================================================")
    print("[*] FinanUNI - Lanzador de Ambas Instancias Web")
    print("    - FinanUNI_Vuln en http://127.0.0.1:5000")
    print("    - FinanUNI_Sec  en http://127.0.0.1:5001")
    print("    Presione Ctrl + C para detener ambas aplicaciones.")
    print("=================================================================")

    proc_vuln = subprocess.Popen([python_exec, "run.py"], cwd=vuln_dir)
    proc_sec = subprocess.Popen([python_exec, "run.py"], cwd=sec_dir)

    try:
        while True:
            time.sleep(1)
            if proc_vuln.poll() is not None:
                print(f"[!] FinanUNI_Vuln termino con codigo {proc_vuln.returncode}")
                break
            if proc_sec.poll() is not None:
                print(f"[!] FinanUNI_Sec termino con codigo {proc_sec.returncode}")
                break
    except KeyboardInterrupt:
        print("\n[*] Deteniendo ambas aplicaciones...")
    finally:
        for proc in (proc_vuln, proc_sec):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("[+] Ambas instancias fueron detenidas correctamente.")

if __name__ == '__main__':
    main()
