# FinanUNI — Molde Inicial de Arquitectura e Interfaces Web

**Práctica Calificada 2 · Seguridad de Software (CBS07)**  
*Universidad Nacional de Ingeniería (UNI) — 2026-II*  
**Versión del avance**: 0.1.0 (Molde estructural y pantallas activas)

---

## 1. Propósito Académico

**FinanUNI** es un proyecto académico diseñado para estudiar de forma práctica y comparativa los principios de *Security by Design*, modelado de amenazas (STRIDE/DREAD) y la corrección de fallas críticas de seguridad de software según los lineamientos del curso CBS07:

1. **SQL Injection (SQLi / CWE-89)** en la búsqueda y filtrado de movimientos financieros.
2. **Insecure Direct Object Reference (IDOR / CWE-639)** en la consulta no autorizada de transferencias.
3. **Integer Overflow (CWE-190)** en la conversión numérica de soles a céntimos procesada por un módulo nativo en C.

El repositorio alberga dos aplicaciones web independientes que operan en paralelo para facilitar su posterior análisis diferencial:
- **`FinanUNI_Vuln`**: Instancia intencionalmente vulnerable para evidenciar los vectores de explotación.
- **`FinanUNI_Sec`**: Instancia corregida que implementará los controles defensivos y validará la mitigación de los riesgos.

> [!NOTE]
> **Alcance de este avance**: Este commit contiene **únicamente la estructura modular, los contratos arquitectónicos y las interfaces web iniciales**. No implementa operaciones financieras reales, conexiones a bases de datos ni lógica de negocio, las cuales se desarrollarán en los siguientes avances según la división de responsabilidades acordada.

---

## 2. URLs y Puertos Asignados

| Aplicación | Puerto | URL Local | Descripción |
| :--- | :--- | :--- | :--- |
| **FinanUNI_Vuln** | `5000` | `http://127.0.0.1:5000` | Instancia vulnerable de laboratorio (cookie `finanuni_vuln_session`). |
| **FinanUNI_Sec** | `5001` | `http://127.0.0.1:5001` | Instancia protegida con controles de seguridad (cookie `finanuni_sec_session`). |

Ambas aplicaciones se ejecutan en *loopback* (`127.0.0.1`) de manera completamente independiente y pueden funcionar simultáneamente.

---

## 3. Instalación de Dependencias y Ejecución

### Requisitos Previos
- Python 3.10 o superior (verificado con Python 3.14).
- Gestor de paquetes `pip`.

### Paso 1: Instalación de Dependencias
Instale los paquetes mínimos requeridos (Flask):
```bash
pip install -r FinanUNI_Vuln/requirements.txt
```
*(Ambas aplicaciones comparten la misma dependencia base en este avance).*

### Paso 2: Ejecución de las Aplicaciones

#### Opción A: Arrancar ambas aplicaciones simultáneamente (Recomendado)
Utilice el script utilitario provisto en la raíz del repositorio:
```bash
python run_both.py
```
Este comando levantará `FinanUNI_Vuln` en el puerto 5000 y `FinanUNI_Sec` en el puerto 5001 al mismo tiempo. Para detener ambas, presione `Ctrl + C`.

#### Opción B: Arrancar cada aplicación por separado
- **Para FinanUNI_Vuln (Puerto 5000):**
  ```bash
  python FinanUNI_Vuln/run.py
  ```
- **Para FinanUNI_Sec (Puerto 5001):**
  ```bash
  python FinanUNI_Sec/run.py
  ```

---

## 4. Qué Funciona Realmente en este Avance

Las siguientes funciones de infraestructura e interfaz se encuentran 100% implementadas y operativas:

1. **Aplicaciones Flask y Enrutamiento**:
   - Creación mediante patrón *Application Factory* (`create_app()`).
   - Configuración individual de puertos (5000 y 5001), secretos y nombres de cookie de sesión.
   - Servido de archivos estáticos (CSS y JavaScript) y plantillas Jinja2.

2. **Cuatro Pantallas Base Activas en Ambas Versiones**:
   - **Inicio de sesión (`/login` o `/`)**: Formulario con campos de usuario y contraseña ficticios.
   - **Consulta de movimientos (`/movimientos`)**: Formulario con filtros de cliente, rango de fechas UTC y montos enteros en soles.
   - **Detalle de transferencia (`/transferencias/detalle`)**: Buscador por identificador numérico de operación.
   - **Formulario de transferencia (`/transferencias/nueva`)**: Formulario con cuenta origen, cuenta destino, monto en soles enteros y nota explicativa de la restricción numérica.
   - **Pantalla de salud (`/health`)**: Tablero visual con el estado de los componentes e inspección de `/api/health`.

3. **Navegación Fluida de Demostración**:
   - Barra de navegación accesible en todo momento para recorrer las pantallas sin requerir autenticación previa ni simular sesiones falsas.
   - Botón directo para alternar entre ambas instancias desde la interfaz.
   - Distintivo visual visible en la cabecera que identifica claramente la versión (`⚠️ VULNERABLE · PUERTO 5000` o `🛡️ SEGURA · PUERTO 5001`).

4. **Manejo de Formularios y Respuestas HTTP 501**:
   - Al enviar cualquiera de los formularios de las pantallas, la interfaz efectúa una petición asíncrona a los endpoints correspondientes de la API (`/api/login`, `/api/movimientos`, `/api/transferencias`).
   - Cada endpoint de negocio responde formalmente con el código de estado **HTTP 501 Not Implemented** y el mensaje: `"Funcionalidad pendiente de implementación"`.
   - El frontend captura este código y muestra una advertencia informativa clara, **sin simular accesos correctos, transferencias ficticias ni saldos actualizados**.

5. **Endpoint de Salud Básico**:
   - `GET /api/health` responde con HTTP 200 y JSON indicando la disponibilidad de la instancia web.

---

## 5. Diferenciación entre Datos Visuales de Muestra y Resultados Reales

Para cumplir con el diseño visual sin recurrir a datos simulados que aparenten funcionalidad inexistente:
- **Datos de muestra de la interfaz**: En las pantallas de consulta de movimientos y detalle de transferencia, la tabla y la ficha muestran ejemplos visuales estáticos (IDs 1051, 1052, 1053) acompañados de una etiqueta destacada:
  > **🏷️ DATOS DE MUESTRA DE LA INTERFAZ**  
  > *Los registros mostrados a continuación son datos estáticos definidos únicamente para previsualizar el diseño de la tabla en esta entrega de molde inicial. No proceden de consultas a la base de datos ni representan resultados del sistema.*
- Ninguno de estos datos proviene de consultas SQL ni de la capa de persistencia.

---

## 6. Funcionalidades que Permanecen Pendientes

Las siguientes funciones **NO** están implementadas y cuentan únicamente con firmas y marcadores `# TODO` en sus respectivos módulos:

- **Autenticación e Identidad**: Verificación de credenciales, hashing con Argon2id, creación y expiración de sesiones servidoras opacas.
- **Autorización y Control de Acceso**: Matriz de permisos RBAC (cliente vs. auditor), denegación por defecto y comprobación de propiedad de recursos contra IDOR.
- **Validación de Entradas**: Validación contextual estricta de tipos, formatos, longitudes y rangos de datos en el servidor.
- **Persistencia**: Conexión activa a SQLite, creación de tablas a partir de `schema.sql` y carga de la semilla reproducible.
- **Operaciones Financieras**: Lógica contable de débito, crédito, cálculo de saldos y confirmación atómica de transferencias.
- **Auditoría Funcional**: Registro persistente de eventos estructurados excluyendo secretos.
- **Motor Numérico en C**: Código fuente C, compilación del ejecutable `conversor_c` y adaptador de subproceso en Python.
- **Vulnerabilidades y Controles**: Inyección SQL, acceso indebido por ID, desbordamiento de enteros y sus respectivas defensas en `FinanUNI_Sec`.

---

## 7. Próximas Tareas según Responsabilidades Acordadas

| Responsable | Alcance de Tareas Inmediatas |
| :--- | :--- |
| **Integrante 1** *(y funciones del 3)* | **Validación e Inyecciones; Identidad, Autorización e Integración:**<br>- Implementar repositorio de consultas de movimientos y evidenciar SQLi concatenada en `Vuln`.<br>- Implementar validación contextual y parametrización en `Sec` (RF04, RF05).<br>- Implementar autenticación Argon2id, sesiones servidoras y RBAC (cliente/auditor) (RF02, RF07).<br>- Implementar control de propiedad de transferencias contra IDOR con respuesta 404 uniforme (RF06). |
| **Integrante 2** *(Compañero)* | **Motor C y Límites Numéricos:**<br>- Implementar el programa C `conversor_c` bajo el contrato `conversor.h` (límite 21,474,836 soles / int32_t) (RF08).<br>- Evidenciar el desbordamiento de enteros (CWE-190) y compilar con detector de comportamiento indefinido.<br>- Programar la validación de precondiciones numéricas en `Sec`.<br>- Diseñar pruebas numéricas y análisis de límites de memoria (T07, T08). |
| **Ambos** | **Integración y Evaluación:**<br>- Integrar la transacción atómica de transferencia conectando Flask, SQLite y el motor C (RF09, RF10).<br>- Auditoría estructurada sin fugas de secretos (RF11).<br>- Ejecución de la matriz de pruebas T01 a T11, revisión cruzada de código y registro crítico del uso de IA. |

---

## 8. Verificación de Infraestructura

Para comprobar que el molde inicial cumple con todos los requisitos y que ningún endpoint o formulario realiza operaciones no autorizadas, ejecute las pruebas unitarias automatizadas:

```bash
# Pruebas en FinanUNI_Vuln
python -m unittest FinanUNI_Vuln/tests/test_scaffold.py

# Pruebas en FinanUNI_Sec
python -m unittest FinanUNI_Sec/tests/test_scaffold.py
```
