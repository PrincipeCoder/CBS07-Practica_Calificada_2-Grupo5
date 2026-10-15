# FinanUNI_Sec — Instancia Segura (Molde Inicial)

**Práctica Calificada 2 · Seguridad de Software (CBS07)**
**Versión**: 0.1.0 (Molde inicial de infraestructura e interfaz)
**URL Local**: `http://127.0.0.1:5001`

---

## 1. Propósito de esta Instancia
`FinanUNI_Sec` es la aplicación corregida y protegida que implementará los controles de seguridad en profundidad:
- **Consultas Parametrizadas (RF05 / S04)** para prevenir SQL Injection.
- **Autorización por Recurso y Denegación por Defecto (RN04 / RF06 / S06)** con respuesta 404 uniforme contra IDOR.
- **Validación Estricta de Rango Numérico (RF08 / S05)** para evitar Integer Overflow en la conversión monetaria en C.
- **Transacciones Atómicas y Registro de Auditoría (RF10 / RF11 / S01)** sin fuga de datos sensibles.

---

## 2. Estado de este Primer Avance
En este primer avance se construye **únicamente el molde inicial**:
- ✅ **Funcionando**:
  - Creación y registro de la aplicación Flask.
  - Servido de las 4 pantallas HTML y recursos estáticos con distintivo visible en puerto 5001.
  - Navegación fluida entre pantallas sin requerir autenticación previa.
  - Endpoint de salud (`/api/health`) activo con respuesta HTTP 200.
  - Manejo de formularios mediante JavaScript que informa el estado pendiente (HTTP 501) sin anunciar operaciones simuladas.
- ⏳ **Pendiente de implementación** (responsabilidad de siguientes etapas):
  - Autenticación segura con hash Argon2id y sesiones servidoras independientes (`finanuni_sec_session`).
  - Consultas parametrizadas en SQLite.
  - Verificación de propiedad en transferencias contra IDOR.
  - Compilación e integración del motor C con comprobación de desborde (`conversor_c`).
  - Pruebas de mitigación y seguridad.

---

## 3. Estructura de Carpetas
```
FinanUNI_Sec/
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
├── run.py              # Punto de entrada de la aplicación (Puerto 5001)
└── requirements.txt    # Dependencias mínimas (Flask)
```

---

## 4. Instalación y Ejecución
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación en el puerto 5001:
   ```bash
   python run.py
   ```
3. Abrir en el navegador:
   `http://127.0.0.1:5001`

---

## 5. Verificación de Rutas
Para ejecutar las pruebas automáticas de infraestructura:
```bash
python -m unittest tests/test_scaffold.py
```
