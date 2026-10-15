# Registro de Interacciones y Uso Crítico de Inteligencia Artificial (DE04)

**Proyecto**: FinanUNI · Seguridad de Software (CBS07)  
**Entregable**: DE04 — Registro de prompts, recomendaciones evaluadas, decisiones de seguridad y pruebas asociadas.

---

## Interacción 1: Algoritmo de Hashing para Contraseñas Ficticias (RN05)

- **Prompt**: ¿Cómo almacenar las contraseñas en SQLite para la autenticación de los clientes Ana, Bruno y Auditor?
- **Recomendación recibida**: Emplear `hashlib.sha256` o el generador por defecto de Flask (`werkzeug.security.generate_password_hash`).
- **Evaluación crítica**:
  - *Inconveniente*: SHA-256 sin sal ni factor de costo es altamente vulnerable a ataques por tablas arcoíris y GPUs. Aunque Werkzeug implementa scrypt o pbkdf2, el requisito explícito no funcional **RN05** exige formalmente el uso de **Argon2id**, el cual ofrece resistencia superior contra ataques acelerados por hardware y canales laterales.
- **Decisión adoptada**: Se instaló e integró la biblioteca estándar `argon2-cffi` con parámetros canónicos (`time_cost=3`, `memory_cost=65536`, `parallelism=4`), garantizando hashes con formato `$argon2id$v=19$...`.
- **Prueba asociada**: `test_t02_login_valido_e_invalido` en `FinanUNI_Vuln` y `test_t02_login_argon2id_csrf_y_separacion` en `FinanUNI_Sec`.

---

## Interacción 2: Mitigación de IDOR y Código de Estado HTTP (AM02 / RF06)

- **Prompt**: ¿Qué código de estado HTTP debe devolverse cuando un cliente autenticado (ej. Ana) intenta consultar una transferencia de otro cliente (ej. 1052 de Bruno)?
- **Recomendación recibida**: Retornar `403 Forbidden` con el mensaje *"No tiene permisos para ver esta transferencia ajena"*.
- **Evaluación crítica**:
  - *Inconveniente*: Retornar `403 Forbidden` revela de forma implícita que el recurso **sí existe** en la base de datos (ataque por enumeración o sondeo de identificadores válidos).
- **Decisión adoptada**: Aplicar el principio de **respuesta uniforme 404 Not Found** (*Resource Not Found*) tanto para transferencias inexistentes como para transferencias ajenas al cliente. Así, un atacante no puede distinguir si el número consultado existe o no. Para el rol auditor, se preserva el acceso legítimo completo.
- **Prueba asociada**: `test_t05_am02_idor_mitigado_404_uniforme` en `FinanUNI_Sec` y `test_comparacion_idor` en `tests/comparacion/test_diferencial.py`.

---

## Interacción 3: Defensa en Profundidad en Consultas de Movimientos (RF05 / AM01)

- **Prompt**: ¿Es suficiente utilizar consultas parametrizadas con `?` en SQLite para neutralizar la inyección SQL en los filtros de búsqueda?
- **Recomendación recibida**: Sí, enlazar directamente `cursor.execute("... WHERE cliente_id = ?", (cliente_id,))` sin validaciones adicionales.
- **Evaluación crítica**:
  - *Inconveniente*: La parametrización evita que la entrada se interprete como código SQL, pero no garantiza la validez semántica ni la integridad del negocio. Una entrada como `"1 OR 1=1"` o un número fuera de rango (`99999999999`) provocaría errores silenciosos o comportamientos imprevistos. Además, el requisito **RF05** y la directriz de *Defensa en Profundidad* exigen validación contextual previa (tipos, rangos, longitudes y formatos).
- **Decisión adoptada**: Implementar un validador contextual estricto (`input_validator.validate_movement_filters`) que comprueba dígitos `[1, 2147483647]`, fechas reales de calendario UTC y coherencia de rangos (`desde <= hasta`, `min <= max`) respondiendo `400 Bad Request` antes de invocar la consulta parametrizada.
- **Prueba asociada**: `test_t03_t04_sqli_neutralizado_en_sec` y `test_t04_validaciones_contextuales_estrictas`.

---

## Interacción 4: Coordinación con el Motor C en Transferencias (RF08 / RF09)

- **Prompt**: Dado que el binario `conversor_c` aún no ha sido provisto por el compañero (Integrante 2), ¿se debería simular la conversión multiplicando `monto_soles * 100` en Python para poder completar la prueba de transferencias?
- **Recomendación recibida**: Implementar una función provisional en Python que multiplique por 100 y retorne éxito 200/201.
- **Evaluación crítica**:
  - *Inconveniente*: Violaría el contrato arquitectónico de la práctica y la instrucción estricta de no adelantar componentes ajenos ni inventar cálculos: *"El adaptador Python–C debe respetar el contrato acordado. Si el motor todavía no está disponible, conserva la operación dependiente como pendiente mediante una respuesta explícita; no inventes un cálculo ni devuelvas éxito"*.
- **Decisión adoptada**: El adaptador comprueba la presencia real del ejecutable en `motor_c/`. Ante su ausencia, detiene de inmediato el flujo financiero y responde formalmente con `HTTP 501 Not Implemented` y el detalle exacto de la dependencia pendiente, garantizando que ningún saldo se altere en la base de datos hasta que el motor en C esté compilado e integrado.
- **Prueba asociada**: `test_t08_motor_c_pendiente_explicitamente` en ambas suites de pruebas.
