# Estado técnico · G01 · 2026-11-15

**Release:** DS01/EXP03, Cerro Azul. Datos sintéticos del grupo, sin transferencia de cifras G05.

M01B fue reconstruido desde las fuentes propias y reproduce los conteos documentados: 3,632 compósitos, 19,734 bloques, 12,367 ROCK, 5,186 AIR, 1,050 PARTIAL y 1,131 OUTSIDE; 2,056 bloques con litología preliminar asignada. Se conservan el CSV íntegro, la QA y el visor 3D.

S11 y S12 tienen generaciones propias con validación técnica `VALIDATED`, manifiestos SHA, informes y visores interactivos. `python -m src.missions.g01 verificar` comprueba las generaciones vigentes. La suite automatizada aprobó 31 pruebas; la simulación de estudiante completó 30 actividades y 47 observaciones, comprobó tres bases SQLite y el ZIP individual; Chrome verificó navegación, filtros, selección de bloque, escenarios y ausencia de errores JavaScript. El entregable grupal incluye las fuentes, modelos y software de esta distribución.

**Límites:** CRS/datum no certificados; la asignación litológica no demuestra continuidad geológica. Los tonelajes con densidad y con ley Cu respaldada son universos distintos. S12 clasifica candidatos académicos y compara A/B; no declara reservas profesionales, pit ni secuencia minera física. La conversación real con Kai en Copilot/PyCharm y su aceptación pedagógica humana siguen pendientes.

`DISTRIBUCION_INICIAL_MANIFEST.json` documenta exclusivamente el commit inicial conceptual; `DISTRIBUCION_FINAL_MANIFEST.json` documenta el contenido IMP-008 actual.
