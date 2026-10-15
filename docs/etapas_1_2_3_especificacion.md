# FinanUNI - Especificación de Requisitos, Arquitectura y Modelo de Amenazas
**Práctica Calificada 2 · Seguridad de Software (CBS07)**
*Etapas 1, 2 y 3 · Versión 1.0 · 14 de octubre de 2026*

## 1. Propósito y Alcance
Desarrollo de dos aplicaciones web locales comparables:
- `FinanUNI_Vuln` en `http://127.0.0.1:5000`: evidencia vulnerabilidades (SQLi, IDOR, Integer Overflow).
- `FinanUNI_Sec` en `http://127.0.0.1:5001`: incorpora controles de mitigación y pruebas correspondientes.

### Responsabilidades
- **Integrante 1 (y funciones del 3)**: Validación y SQLi; autenticación; RBAC y propiedad; integración de API e interfaz.
- **Integrante 2**: Motor C; demostración y corrección de overflow; pruebas numéricas y análisis de memoria.
- **Ambos**: Diseño, revisión cruzada, amenazas, evaluación de IA, pruebas integradas, presentación y video.

## 2. Requisitos y Contratos Principales
- **RF01**: Ejecución simultánea en puertos 5000 y 5001, con datos y sesiones separados.
- **RF02 / RF07**: Autenticación y RBAC (cliente vs. auditor).
- **RF04 / RF05**: Consulta de movimientos y mitigación de SQLi mediante parametrización y validación de tipos/rangos.
- **RF06**: Detalle de transferencia y mitigación de IDOR mediante validación de propiedad y pertenencia al recurso.
- **RF08**: Invocación a motor en C para conversión de soles enteros a céntimos (int32_t, límite 21474836 soles).
- **RF10**: Atomicidad de transferencias y consistencia contable.
- **RF11**: Auditoría sin registrar contraseñas ni datos sensibles.

## 3. Modelo de Amenazas (STRIDE & DREAD)
- **AM01 (SQLi)**: DREAD 8.8 (Alta) - Inyección en filtros de movimientos.
- **AM02 (IDOR)**: DREAD 8.6 (Alta) - Consulta no autorizada de transferencias por manipulación de ID.
- **AM03 (Integer Overflow)**: DREAD 6.9 (Media) - Desbordamiento de enteros en conversión monetaria C.
- **AM04 (Identidad)**: DREAD 9.0 (Alta) - Suplantación de identidad o sesión.
- **AM05 a AM08**: Auditoría manipulable, agotamiento de recursos, atomicidad parcial y CSRF.
