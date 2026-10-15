/*
 * FinanUNI_Vuln - Motor C (Vulnerable)
 * Asignatura: Seguridad de Software (CBS07) - UNI
 * Responsable: Integrante 2
 *
 * Propósito Académico:
 * Demostrar la ausencia de controles de precondición aritmética ante multiplicaciones
 * que sobrepasan el rango del tipo entero con signo int32_t (CWE-190: Integer Overflow).
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <limits.h>
#include "conversor.h"

/*
 * FUNCIÓN VULNERABLE:
 * Multiplica directamente por 100 sin validar si el resultado sobrepasará INT32_MAX.
 * En C, el desbordamiento de enteros con signo es Comportamiento Indefinido
 * (Undefined Behavior). En compilaciones estándar x86_64 suele ocurrir un wraparound de bits,
 * generando números negativos o montos financieros totalmente distorsionados.
 */
int32_t convertir_centimos(int32_t soles) {
    // AUSENCIA DELIBERADA DE CONTROL: No se evalúa el límite antes de multiplicar.
    return soles * 100;
}

int main(int argc, char *argv[]) {
    // 1. Control de presencia de argumento exacto
    if (argc != 2) {
        printf("{\"estado\": \"ERROR\", \"motivo\": \"INVALID_INPUT\"}\n");
        return 2;
    }

    // 2. Parseo correcto de texto a entero largo
    char *endptr;
    errno = 0;
    long val = strtol(argv[1], &endptr, 10);

    // Se rechaza la entrada si la cadena no es decimal válida o contiene caracteres extra
    if (errno != 0 || *endptr != '\0' || argv[1] == endptr) {
        printf("{\"estado\": \"ERROR\", \"motivo\": \"INVALID_INPUT\"}\n");
        return 2;
    }

    // Estrechamiento implícito a 32 bits y multiplicación vulnerable
    int32_t soles = (int32_t)val;
    int32_t centimos = convertir_centimos(soles);

    // Salida estructurada según contrato CLI-JSON (Código de salida 0)
    printf("{\"estado\": \"OK\", \"centimos\": %d}\n", centimos);
    return 0;
}