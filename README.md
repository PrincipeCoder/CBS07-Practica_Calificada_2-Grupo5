# FinanUNI — Proyecto Académico de Seguridad de Software

**Práctica Calificada 2 · Seguridad de Software (CBS07)**  
*Universidad Nacional de Ingeniería (UNI) — 2026-II*  
**Versión actual**: 0.2.0 (Etapas 5 y 6 — Responsabilidades del Integrante 1 y Funciones del Integrante 3)

---

## 1. Propósito Académico

**FinanUNI** es un laboratorio comparativo para el estudio de vulnerabilidades y controles de seguridad en aplicaciones financieras web. El proyecto implementa dos versiones completas e independientes en paralelo:

- **`FinanUNI_Vuln`** (`http://127.0.0.1:5000`): Evidencia vulnerabilidades críticas de software en un entorno local controlado:
  - **SQL Injection (SQLi / AM01 / CWE-89)** en la búsqueda y filtrado de movimientos.
  - **Insecure Direct Object Reference (IDOR / AM02 / CWE-639)** en la consulta de transferencias por identificador omitiendo autorización.
- **`FinanUNI_Sec`** (`http://127.0.0.1:5001`): Implementa los controles defensivos correspondientes:
  - **Consultas 100% parametrizadas y validación contextual de entradas (RF05)**.
  - **Control de acceso por recurso (RBAC) con respuesta HTTP 404 uniforme contra IDOR (RF06 / RN04)**.
  - **Protección contra Cross-Site Request Forgery (CSRF / AM08)**.
  - **Hashing de contraseñas con Argon2id (RN05)** y sesiones servidoras independientes.

---

## 2. Semilla Reproducible del Laboratorio

Ambas aplicaciones se inicializan automáticamente con la semilla acordada en la Etapa 2:

### Usuarios y Credenciales Ficticias
| ID | Usuario | Contraseña Ficticia | Rol | Propósito en el Laboratorio |
| :---: | :---: | :---: | :---: | :--- |
| `1` | `ana` | `ana123` | `cliente` | Titular de la cuenta 101. Consulta movimientos propios e intenta IDOR hacia 1052. |
| `2` | `bruno` | `bruno123` | `cliente` | Titular de las cuentas 102 y 103. Titular de la transferencia privada 1052. |
| `3` | `auditor` | `auditor123` | `auditor` | Rol de auditoría con lectura global de transferencias y prohibición de transferir. |

### Cuentas Bancarias
- **Cuenta 101**: Titular Ana, Saldo inicial: `5,000,000` céntimos (S/ 50,000.00).
- **Cuenta 102**: Titular Bruno, Saldo inicial: `3,000,000` céntimos (S/ 30,000.00).
- **Cuenta 103**: Titular Bruno, Saldo inicial: `1,000,000` céntimos (S/ 10,000.00).

### Transferencias Históricas
- **#1051**: Cuenta 101 ➔ Cuenta 102 por S/ 100.00 (10,000 céntimos). **Participan Ana y Bruno**.
- **#1052**: Cuenta 102 ➔ Cuenta 103 por S/ 200.00 (20,000 céntimos). **Exclusiva de Bruno (AJENA a Ana)**.
- **#1053**: Cuenta 103 ➔ Cuenta 102 por S/ 50.00 (5,000 céntimos). **Exclusiva de Bruno**.

---

## 3. Instalación y Ejecución

### Dependencias
Instale los paquetes requeridos (Flask y Argon2-cffi):
```bash
pip install -r FinanUNI_Vuln/requirements.txt
```

### Ejecutar Ambas Aplicaciones en Simultáneo
```bash
python run_both.py
```
- **FinanUNI_Vuln**: `http://127.0.0.1:5000` (Cookie: `finanuni_vuln_session`)
- **FinanUNI_Sec**: `http://127.0.0.1:5001` (Cookie: `finanuni_sec_session`)

*(Presione `Ctrl + C` para detener ambos servidores limpiamente).*

---

## 4. Verificación de Vulnerabilidades y Controles

### A. Demostración de SQL Injection (AM01 / CWE-89)
1. Inicie sesión como **Ana** (`ana` / `ana123`) en `FinanUNI_Vuln` (`:5000`).
2. Diríjase a **Movimientos** e ingrese en el filtro *ID de Cliente*: `1 OR 1=1`.
3. **Resultado en Vuln**: La consulta concatenada se altera y la aplicación expone las 3 transferencias de la base de datos (1051, 1052 y 1053).
4. Pruebe el mismo filtro en `FinanUNI_Sec` (`:5001`):
5. **Resultado en Sec**: El validador contextual detecta caracteres no numéricos y rechaza la petición con **HTTP 400 Bad Request**, protegiendo la base de datos.

### B. Demostración de IDOR (AM02 / CWE-639)
1. Inicie sesión como **Ana** en `FinanUNI_Vuln` (`:5000`).
2. Diríjase a **Detalle** y busque el ID `1051` (transferencia legítima de Ana ➔ HTTP 200).
3. Cambie el ID a `1052` (transferencia entre cuentas 102 y 103 de Bruno).
4. **Resultado en Vuln**: El endpoint expone con **HTTP 200** la transferencia privada de Bruno porque omitió verificar la titularidad.
5. Inicie sesión como **Ana** en `FinanUNI_Sec` (`:5001`) y consulte `1052`:
6. **Resultado en Sec**: El servidor verifica la participación y retorna **HTTP 404 Recurso no encontrado** uniforme, impidiendo el acceso y la enumeración de identificadores.
7. Inicie sesión como **Auditor** en `FinanUNI_Sec` y consulte `1052`: la consulta es permitida (HTTP 200) según la matriz RBAC.

### C. Coordinación con el Motor en C
- El adaptador en Python respeta el contrato `motor_c/conversor.h`.
- Mientras el binario `conversor_c` no esté compilado por el Integrante 2, cualquier solicitud de transferencia responde explícitamente con **HTTP 501**, garantizando que ningún saldo se altere sin el cálculo nativo validado.

---

## 5. Ejecución de Pruebas Automatizadas

```bash
# 1. Pruebas de la versión vulnerable (Etapa 5): login, SQLi e IDOR
python -m unittest FinanUNI_Vuln/tests/test_etapa5.py

# 2. Pruebas de la versión corregida (Etapa 6): Argon2id, CSRF, validación, 404 uniforme y RBAC
python -m unittest FinanUNI_Sec/tests/test_etapa6.py

# 3. Pruebas diferenciales comparativas directas (Vuln vs. Sec)
python -m unittest tests/comparacion/test_diferencial.py
```
*(Las 18 pruebas unitarias e integradas se ejecutan con resultados exitosos).*

---

## 6. Documentación Adicional
- [docs/etapas_1_2_3_especificacion.md](file:///c:/Users/ANGHELOKENEDYPRINCIP/Documents/GitHub/CBS07-Practica_Calificada_2-Grupo5/docs/etapas_1_2_3_especificacion.md): Especificación de Requisitos, Arquitectura y Modelo de Amenazas.
- [docs/registro_ia.md](file:///c:/Users/ANGHELOKENEDYPRINCIP/Documents/GitHub/CBS07-Practica_Calificada_2-Grupo5/docs/registro_ia.md): Registro crítico de prompts, evaluaciones y decisiones adoptadas (DE04).
