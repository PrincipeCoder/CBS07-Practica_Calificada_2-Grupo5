"""
Punto de entrada para la aplicación FinanUNI_Vuln (Puerto 5000).
"""
import os
from app import create_app
from app.config import VulnConfig

app = create_app(VulnConfig)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    print(f"[*] Iniciando FinanUNI_Vuln en http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
