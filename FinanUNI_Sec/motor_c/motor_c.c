/*
 * FinanUNI_Sec - Motor C (Corregido / Seguro)
 * Asignatura: Seguridad de Software (CBS07) - UNI
 * Responsable: Integrante 2
 *
 * Propósito:
 * Prevenir el Integer Overflow (CWE-190) mediante la verificación estricta de 
 * PRECONDICIONES MATEMÁTICAS antes de realizar cualquier operación aritmética.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <errno.h>
#include "conversor.h"

/*
 * DERIVACIÓN MATEMÁTICA DEL LÍMITE:
 * Para un tipo entero de 32 bits con signo (int32_t):
 * - INT32_MAX =  2,147,483,647
 * - INT32_MIN = -2,147,483,648
 *
 * Para garantizar que (soles * 100) no desborde INT32_MAX ni INT32_MIN:
 * - MAX_SOLES_PERMITIDOS = INT32_MAX / 100 =  21,474,836 soles  (2,147,483,600 céntimos)
 * - MIN_SOLES_PERMITIDOS = INT32_MIN / 100 = -21,474,836 soles (-2,147,483,600 céntimos)
 */
#define MAX_SOLES_PERMITIDOS (INT32_MAX / 100) //  21,474,836
#define MIN_SOLES_PERMITIDOS (INT32_MIN / 100) // -21,474,836

int32_t convertir_centimos(int32_t soles) {
    return soles * 100;
}

int main(int argc, char *argv[]) {
    // 1. Validar presencia estricta de un único argumento por CLI
    if (argc != 2) {
        printf("{\"estado\": \"ERROR\", \"motivo\": \"INVALID_INPUT\"}\n");
        return 2;
    }

    // 2. Parseo sintáctico de la entrada con strtol
    char *endptr;
    errno = 0;
    long val = strtol(argv[1], &endptr, 10);

    // Comprobar error de conversión, caracteres sobrantes o cadena vacía
    if (errno != 0 || *endptr != '\0' || argv[1] == endptr) {
        printf("{\"estado\": \"ERROR\", \"motivo\": \"INVALID_INPUT\"}\n");
        return 2;
    }

    // 3. Comprobar que el valor no desborda la capacidad física del tipo int32_t antes de estrechar
    if (val > INT32_MAX || val < INT32_MIN) {
        printf("{\"estado\": \"ERROR\", \"motivo\": \"OUT_OF_RANGE\"}\n");
        return 3;
    }

    // 4. PRECONDICIÓN MATEMÁTICA: Validar rango antes de efectuar la multiplicación
    if (val > MAX_SOLES_PERMITIDOS || val < MIN_SOLES_PERMITIDOS) {
        printf("{\"estado\": \"ERROR\", \"motivo\": \"OUT_OF_RANGE\"}\n");
        return 3;
    }

    // Operación completamente segura garantizada por la precondición
    int32_t soles = (int32_t)val;
    int32_t centimos = convertir_centimos(soles);

    // Salida estandarizada según contrato (Código de salida 0)
    printf("{\"estado\": \"OK\", \"centimos\": %d}\n", centimos);
    return 0;
}