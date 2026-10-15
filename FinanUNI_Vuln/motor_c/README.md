# Motor C - Conversor Monetario

Este directorio reserva el espacio y contrato para el ejecutable nativo en C del motor numérico de **FinanUNI**.

## Responsabilidad
- **Responsable**: Integrante 2 (Compañero).
- **Desafío técnico**: Demostración y corrección de Integer Overflow (CWE-190 / AM03 / RF08).

## Contrato de Invocación e Interfaz
- **Invocación desde Python**: Ejecutable local invocado directamente (sin shell) pasando un argumento decimal.
- **Rango Seguro**:
  - `INT32_MAX = 2147483647`
  - Límite máximo en soles: `21474836` soles (`21474836 * 100 = 2147483600 <= INT32_MAX`).
  - Entradas de `21474837` o superiores desbordan el tipo firmado de 32 bits.
- **Salida esperada**:
  - Caso exitoso (código 0): `{"estado": "OK", "centimos": 10000}`
  - Error de entrada (código 2): `{"estado": "ERROR", "motivo": "INVALID_INPUT"}`
  - Desborde fuera de rango (código 3): `{"estado": "ERROR", "motivo": "OUT_OF_RANGE"}`
- **Límites operativos**: Timeout de 1 segundo y respuesta máxima de 1 KiB.

## Estado de este Avance
- **Estado**: Pendiente de implementación y compilación.
- Conforme a las directrices de la entrega inicial, **no se incluye ningún ejecutable compilado ni simulado**. La lógica de conversión se implementará en la siguiente fase de desarrollo.
