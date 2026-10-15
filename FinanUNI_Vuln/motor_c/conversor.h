/**
 * @file conversor.h
 * @brief Contrato del motor numérico en C para conversión monetaria.
 *
 * Proyecto: FinanUNI (Seguridad de Software CBS07)
 * Responsabilidad: Integrante 2 (Demostración y corrección de overflow CWE-190).
 *
 * ESPECIFICACIÓN DEL CONTRATO:
 * - Unidad y rango: Convierte soles enteros a céntimos usando int32_t.
 * - Límite de int32_t: INT32_MAX = 2147483647.
 * - Máximo entero multiplicable por 100 sin desborde: floor(2147483647 / 100) = 21474836 soles.
 * - Salida exitosa: Código de salida 0 y JSON en una línea: {"estado": "OK", "centimos": <int>}
 * - Error de entrada: Código de salida 2 y JSON: {"estado": "ERROR", "motivo": "INVALID_INPUT"}
 * - Desbordamiento (out of range): Código de salida 3 y JSON: {"estado": "ERROR", "motivo": "OUT_OF_RANGE"}
 *
 * En este primer avance estructural, este archivo documenta el contrato y las firmas.
 * El ejecutable compilado permanece pendiente para el desarrollo de la Etapa 4 por el Integrante 2.
 */

#ifndef CONVERSOR_H
#define CONVERSOR_H

#include <stdint.h>

#define MAX_SOLES_SEGURO 21474836
#define MULTIPLICADOR_CENTIMOS 100

typedef enum {
    CONVERSION_OK = 0,
    ERROR_INVALID_INPUT = 2,
    ERROR_OUT_OF_RANGE = 3
} ConversionStatus;

typedef struct {
    ConversionStatus status;
    int32_t centimos;
    const char *error_msg;
} ConversionResult;

/**
 * @brief Convierte soles enteros a céntimos verificando precondiciones aritméticas.
 *
 * @param soles_input Monto en soles enteros recibido como argumento decimal.
 * @return ConversionResult con estado y valor calculado.
 *
 * TODO: Implementar por el Integrante 2 en siguientes commits.
 */
ConversionResult convertir_soles_a_centimos(int64_t soles_input);

#endif /* CONVERSOR_H */
