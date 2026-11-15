# Modelo de bloques de recursos ACADÉMICO

Corrida `03b42697a864bb6f88e8`. G01 DS01/EXP03; 19,734 celdas.

Cu estimado: 395 bloques a 75 m; 386 a 50 m. Densidad estimada: 2047. Tonelaje cuantificable: 34208415.381075 t en 2047 bloques. Con Cu y tonelaje: 392 bloques, 6474962.972632 t.

## Trazabilidad

Ensayes originales → compósitos por longitud y contacto → IDW² por código preliminar. Mo y Au se reconstruyen desde ensayes; Cu se concilia con M01. Cada estimación conserva IDs, distancias, pesos y sondajes. Densidad usa desurvey M01 y mediciones íntegramente contenidas en un dominio. Residuales se preservan en QA. Volumen: recorte de TIN por huella y límites verticales; integración analítica de planos. Se conserva el estado topográfico M01B heredado por separado. Nulo no significa cero.

## Supuestos y límites

- Litología preliminar; continuidad entre sondajes no demostrada.
- Estimación en centro como proxy académico; soporte volumétrico no corregido.
- CRS/datum topográfico no documentados; compatibilidad local heredada como supuesto.
- Incertidumbre de estimación no cuantificada por IDW².

## Verificación

`s11_validation.json` contiene controles ejecutados. La comparación manual .60 % / 2.64 t/m³ es un microcaso PT-01, no un bloque G01. La tabla completa respalda los totales; el 3D reduce contexto si excede 6000 cajas.
