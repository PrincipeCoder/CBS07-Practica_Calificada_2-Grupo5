"""
Punto de entrada para la aplicación FinanUNI_Sec (Puerto 5001).
"""
import os
from app import create_app
from app.config import SecConfig

app = create_app(SecConfig)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '127.0.0.1')
    print(f"[*] Iniciando FinanUNI_Sec en http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
