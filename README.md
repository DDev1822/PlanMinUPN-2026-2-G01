# PlanMinUPN 2026-2 · G01 Cerro Azul

Distribución independiente del grupo G01, release académico **DS01/EXP03**. Árbol preparado desde [`piero0123333-sketch/PlanMinUPN-01`](https://github.com/piero0123333-sketch/PlanMinUPN-01/commit/a28fc1b378991f0c2a07581f06a7d02d4fc31033) en el SHA `a28fc1b378991f0c2a07581f06a7d02d4fc31033`. Este repositorio empieza con un commit propio; no importa el historial del equipo anterior.

## Inicio

1. Clona este repositorio y abre su raíz en PyCharm.
2. Usa Python 3.12. Crea un entorno virtual e instala `python -m pip install -r requirements.txt`.
3. Ejecuta `python -m pytest -q` para comprobar la distribución.
4. Selecciona **Kai Planeamiento** desde `.github/agents/kai-planeamiento.agent.md` en Copilot. Consulta `AGENTS.md` y la guía del grupo.

Los datos fuente están en `data/raw/`. El visor M01 y sus salidas pertenecen a este grupo; esta distribución no acredita un M01B cuantitativo. `.kai_local/` contiene progreso individual local y no debe publicarse.

## Alcance disponible

`docs/learning/GUIA_KAI_COMPARTIDA.md` y `kai/recorrido_academico.py` ofrecen 8 actividades E1, 16 S11 y 6 S12 como **teoría conceptual**. El progreso se conserva localmente por alias en SQLite y se exporta a Excel. El controlador comprueba estructura y secuencia; la valoración del razonamiento del estudiante corresponde al tutor.

Este grupo no tiene bajo IMP-008 un producto S11/S12 cuantitativo propio verificado. Tampoco están adaptadas la ficha E1 de 21 observaciones, la aplicación de 26 ni la entrega individual completa. No uses números, bloques o escenarios de G05 para suplirlos. Los modelos M01/M01B que sí existan son del proyecto Cerro Azul y conservan sus límites técnicos.

La aceptación conversacional real de Kai y la revisión visual interactiva están pendientes.
