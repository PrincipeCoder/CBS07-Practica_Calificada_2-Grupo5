# FinanUNI_Vuln — Instancia Vulnerable (Molde Inicial)

**Práctica Calificada 2 · Seguridad de Software (CBS07)**
**Versión**: 0.1.0 (Molde inicial de infraestructura e interfaz)
**URL Local**: `http://127.0.0.1:5000`

---

## 1. Propósito de esta Instancia
`FinanUNI_Vuln` es el laboratorio controlado que posteriormente evidenciará las vulnerabilidades de la práctica:
- **SQL Injection (SQLi / AM01 / CWE-89)** en la búsqueda de movimientos.
- **Insecure Direct Object Reference (IDOR / AM02 / CWE-639)** en la consulta de transferencias por identificador.
- **Integer Overflow (AM03 / CWE-190)** en el motor numérico de conversión en C.

> [!WARNING]
> Esta aplicación es un laboratorio de ciberseguridad estrictamente académico y local. Jamás debe ser expuesta a Internet ni desplegada en entornos productivos.

---

## 2. Estado de este Primer Avance
En este primer avance se construye **únicamente el molde inicial**:
- ✅ **Funcionando**:
  - Creación y registro de la aplicación Flask.
  - Servido de las 4 pantallas HTML y recursos estáticos.
  - Navegación fluida entre pantallas sin requerir autenticación previa.
  - Endpoint de salud (`/api/health`) activo con respuesta HTTP 200.
  - Manejo de formularios mediante JavaScript que informa el estado pendiente (HTTP 501) sin anunciar operaciones simuladas.
- ⏳ **Pendiente de implementación** (responsabilidad de siguientes etapas):
  - Autenticación y sesiones de servidor.
  - Hashing de contraseñas con Argon2id.
  - Consultas y persistencia en SQLite.
  - Lógica financiera de transferencias y actualización de saldos.
  - Compilación e integración del motor C (`conversor_c`).
  - Vulnerabilidades y exploits específicos.

---

## 3. Estructura de Carpetas
```
FinanUNI_Vuln/
├── app/
│   ├── audit/          # Registro de auditoría (firmas preparadas)
│   ├── database/       # Conexión SQLite y schema.sql
│   ├── repositories/   # Repositorios de usuarios, cuentas y transferencias
│   ├── routes/         # Rutas web (HTML) y API REST (HTTP 501)
│   ├── security/       # Módulos de validación, RBAC, criptografía y CSRF
│   ├── services/       # Orquestación de casos de uso y adaptador a motor C
│   ├── static/         # Archivos CSS y JavaScript
│   └── templates/      # Plantillas Jinja2 de las pantallas
├── instance/           # Base de datos SQLite (excluida de Git)
├── logs/               # Registros locales de auditoría (excluidos de Git)
├── motor_c/            # Contrato del motor C (conversor.h y README)
├── tests/              # Pruebas unitarias de rutas e infraestructura
├── run.py              # Punto de entrada de la aplicación
└── requirements.txt    # Dependencias mínimas (Flask)
```

---

## 4. Instalación y Ejecución
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación en el puerto 5000:
   ```bash
   python run.py
   ```
3. Abrir en el navegador:
   `http://127.0.0.1:5000`

---

## 5. Verificación de Rutas
Para ejecutar las pruebas automáticas de infraestructura:
```bash
python -m unittest tests/test_scaffold.py
```
