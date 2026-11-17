# Punto de revisión pedagógica · aplicación S11/S12 G01

**Estado:** observación documentada el 2026-11-16; sin cambio de contrato, preguntas, validador, registros ni entregables de aplicación. DD aprobó la ficha E1 V2 y pidió conservar las 26 observaciones S11/S12 en esta intervención.

## Hallazgo comprobado

El catálogo vigente de `kai/aplicacion_g01.py` genera 13 campos S11 y 13 S12 vinculados a las corridas verificadas G01 (`03b42697a864bb6f88e8` y `6a0abc5cdd8fa86ee4a0`). Las **26 consignas** usan el patrón «¿qué valor observas para…?». El validador comprueba valor numérico esperado, unidad y presencia del número en la respuesta literal; no exige una interpretación minera de ese resultado. Por tanto, las 26 son observaciones de lectura de producto, aunque varias pueden ser útiles para aprender a navegar el visor y distinguir unidades.

| Conjunto | Campos | Observación para revisión |
|---|---|---|
| S11 · resumen (6) | `S11.CU75`, `S11.CU50`, `S11.DENSIDAD`, `S11.CUANTIFICADOS`, `S11.TONELAJE`, `S11.CU_T` | Lectura sucesiva de conteos y tonelaje ya calculados. Revisar cuáles aportan una comparación de soporte y cuáles repiten tarjetas o el resumen. |
| S11 · bloque (7) | `S11.B.CU`, `S11.B.RHO`, `S11.B.V`, `S11.B.T`, `S11.B.H`, `S11.B.MO`, `S11.B.AU` | Lectura repetida de propiedades del mismo bloque. Puede servir para ubicar unidades y respaldo, pero la respuesta aceptada solo repite cifras. |
| S12 · resumen y escenarios (11) | `S12.ORE_N`, `S12.WASTE_N`, `S12.UNKNOWN`, `S12.ORE_T`, `S12.WASTE_T`, `S12.MINE`, `S12.PLANT`, `S12.TRUCK_A`, `S12.TRUCK_B`, `S12.CAPEX`, `S12.OPEX` | Varias cifras ya aparecen en tarjetas o tabla A/B; incluso la diferencia CAPEX se solicita como valor observado. Revisar si se debe pedir relación, límite o decisión sustentada. |
| S12 · bloque (2) | `S12.B.ALLOC`, `S12.B.OPEX` | Lectura de asignación y OPEX del mismo bloque; no se pide explicar el significado de la asignación proporcional. |

**Decisión pendiente, separada de esta intervención:** DD podrá decidir posteriormente si alguna observación debe mantenerse como lectura instrumental, incorporarse como contexto verificado, o reformularse para evaluar interpretación. Cualquier cambio exigirá contrato y pruebas propios, conservación de respuestas anteriores y una autorización específica. Este hallazgo no modifica el requisito vigente de 26 observaciones ni autoriza saltarlas o rellenarlas automáticamente.

**Corrección visual posterior:** las 26 lecturas tienen ahora una tarjeta en `RESULTADOS_G01.html` con valor, nombre, unidad y modelo; los nueve campos de bloque se consultan mediante un buscador visual. Kai recibe el dato verificado y el vínculo a la tarjeta correspondiente. Esta corrección cambia la forma de consultar los resultados, no el catálogo ni el criterio de evaluación de las 26 observaciones.
