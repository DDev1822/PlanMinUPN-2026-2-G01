# Kai Planeamiento · G01 · Cerro Azul

![DrillStone](../assets/L1.png)

**Release:** DS01/EXP03, datos sintéticos. **Malla:** 25 × 25 × 10 m; 19,734 celdas. **Sondajes:** 32. **Compósitos:** 3632.

El recorrido tiene 30 actividades: 8 de E1, 16 de S11 y 6 de S12. Kai explica, pregunta una decisión y su razón, espera la respuesta, contrasta la evidencia y solo entonces avanza. El tutor valora el contenido de la respuesta; el registro controla orden y persistencia, no aprueba semánticamente.

## Comenzar o regresar

El estudiante puede decir «quiero empezar» o «quiero continuar». Kai reconoce Cerro Azul y pide un alias pseudónimo solo si falta; no necesita nombre legal ni correo. Con el alias, consulta internamente `inicio ALIAS` del controlador: una persona nueva recibe E1.01 y quien vuelve recupera su actividad pendiente. Kai enseña el concepto con lenguaje natural, presenta una situación minera, formula una sola pregunta y espera la respuesta. Las operaciones técnicas son del agente; el estudiante no prepara JSON ni ejecuta Python.

Una respuesta insuficiente se registra como `REQUIERE_REFUERZO` y conserva la actividad. Una explicación propia que cumpla el criterio puede registrarse como `DEMOSTRADO` antes de avanzar. No se inventan observaciones de visores. La lectura de modelos se reserva para la actividad que los necesite.

## Datos y modelos propios

- E1: `data/raw/`, `data/processed/`, ocho competencias con evidencia del estudiante, ficha V2 de 21 datos documentales verificados y visor M01B. La ficha V1 y sus registros anteriores permanecen separados.
- M01B: Malla 25 × 25 × 10 m; litología por distancia a segmentos finitos ≤ 26,926 m. Los conteos P2–P4 reproducen el registro previo de G01.
- S11: IDW² de Cu/Mo/Au y densidad bajo las reglas PT-01, con vecinos, radios, litología preliminar y faltantes explícitos. El modelo de bloques completo y el manifiesto se encuentran bajo `outputs/g01_s11/`.
- S12: clasificación académica y escenarios A/B vinculados a la generación S11 del mismo grupo. No hay pit, secuencia física ni reservas profesionales. Productos bajo `outputs/g01_s12/`.
- Aplicación: 13 observaciones S11 y 13 S12, conciliadas con los productos verificados. Los estados y respuestas viven en `.kai_local/` y están excluidos de Git.

La consulta estudiantil `docs/learning/RESULTADOS_G01.html` muestra las 26 lecturas con unidad y permite localizar cualquier bloque de la generación G01. El controlador adjunta al campo pendiente `consulta_estudiantil` y `dato_verificado` para que Kai oriente al estudiante a la tarjeta exacta. Los visores 3D estudiantiles se derivan de los modelos validados sin modificar las generaciones ni sus manifiestos. La lectura numérica de aplicación no constituye por sí sola interpretación minera; su revisión pedagógica está documentada por separado.

## Operación

El controlador `kai/recorrido_g01.py` ofrece `py -3 kai/recorrido_g01.py inicio ALIAS` para abrir o retomar el turno. Las operaciones posteriores procesan solicitudes JSON internas en `.kai_solicitud_recorrido_g01.json` con `py -3 kai/recorrido_g01.py procesar-pendiente`. `estado_ficha_e1` consulta la ficha V2; `responder_ficha_e1` ya no acepta respuestas de copia. `estado_aplicacion` / `responder_aplicacion` conservan las 26 observaciones S11/S12; `entregar_individual` exige ocho competencias E1, los 21 datos documentales verificados, comprensión posterior, aplicación y productos grupales vigentes. Los 21 datos no son 21 demostraciones del alumno.

La secuencia pedagógica es **comprender → predecir → ejecutar → interpretar → validar → avanzar**. Los ejemplos teóricos de métodos no sustituyen la lectura de los modelos propios. Las respuestas reales y la aceptación conversacional mediante Copilot/PyCharm requieren comprobación humana separada.

## Límites

La topografía y los collars coinciden en las coordenadas locales del release, pero no existe certificación formal de CRS/datum. La asignación litológica es preliminar; cercanía no demuestra continuidad. Los resultados son académicos, con datos sintéticos. Los tonelajes con densidad y los tonelajes con Cu respaldado son poblaciones distintas. Los campos ausentes siguen ausentes.

![DrillStone · símbolo](../assets/L3.png)
