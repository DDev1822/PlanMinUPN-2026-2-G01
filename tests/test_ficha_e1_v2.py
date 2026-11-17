"""Los 21 datos de la ficha son contexto, no respuestas inventadas del alumno."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import sqlite3
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kai"))
controller = importlib.import_module("recorrido_g01")
legacy = controller.e1


@pytest.fixture
def private_data(tmp_path, monkeypatch):
    root = tmp_path / "alumnos"
    monkeypatch.setattr(controller, "DATA", root)
    monkeypatch.setattr(controller.theory, "DATA", root)
    monkeypatch.setattr(legacy, "DATA", root)
    return root


def test_contexto_automatico_no_finge_respuestas(private_data):
    alias = "AlumnoDemo"
    turn = controller.start_turn(alias)
    assert turn["actividad_id"] == "E1.01"
    assert turn["contexto_verificado"][0]["id"] == "DATOS.SONDAJES"
    assert turn["contexto_verificado"][0]["valor"] == 32
    assert turn["contexto_verificado"][0]["procedencia"] == "SYSTEM_VERIFIED"
    assert "sondajes" not in turn["pregunta_principal"].lower()
    state = controller.process({"operacion": "estado", "alumno": alias})
    ficha = state["ficha_e1"]
    assert ficha["version"] == 2
    assert ficha["verified_fields"] == 3 and ficha["total_fields"] == 21
    assert "answered" not in ficha
    assert ficha["competencies_demonstrated"] == 0
    assert ficha["complete"] is False
    assert ficha["pending"] is None
    with sqlite3.connect(private_data / alias / "ficha_individual_v2.sqlite") as db:
        rows = db.execute("SELECT field_id,origin,evidence_event_id FROM campos_v2 ORDER BY field_id").fetchall()
    assert {row[0] for row in rows} == {"PROYECTO.NOMBRE", "PROYECTO.DATASET", "PROYECTO.RELEASE"}
    assert all(row[1] == "SYSTEM_VERIFIED" and row[2] is None for row in rows)
    with pytest.raises(ValueError):
        controller.process({"operacion": "responder_ficha_e1", "alumno": alias,
                            "campo": "DATOS.SONDAJES", "respuesta_literal": "32", "valor_propuesto": 32})


def test_cifra_se_vincula_a_evidencia_real_y_error_no_avanza(private_data):
    alias = "AlumnoDemo"
    controller.start_turn(alias)
    controller.process({"operacion": "registrar", "alumno": alias, "actividad": "E1.01",
                        "estado": "REQUIERE_REFUERZO", "respuesta": "Sí, basta un ensayo alto.",
                        "criterio_observado": "Aún generaliza un dato aislado.", "tipo_evidencia": "ERROR_O_DUDA"})
    assert controller.process({"operacion": "estado", "alumno": alias})["ficha_e1"]["verified_fields"] == 3
    literal = "No aprobaría todo el depósito porque una muestra aislada no tiene soporte para representarlo."
    state = controller.process({"operacion": "registrar", "alumno": alias, "actividad": "E1.01",
                                "estado": "DEMOSTRADO", "respuesta": literal,
                                "criterio_observado": "Identifica límite del soporte local.",
                                "tipo_evidencia": "RAZONAMIENTO_PROPIO"})
    assert state["actividad_actual"] == "E1.02"
    assert state["ficha_e1"]["verified_fields"] == 4
    with sqlite3.connect(private_data / alias / "ficha_individual_v2.sqlite") as db:
        field = db.execute("SELECT value_json,origin,evidence_event_id FROM campos_v2 WHERE field_id='DATOS.SONDAJES'").fetchone()
    with sqlite3.connect(private_data / alias / "teoria_v2.sqlite") as db:
        event = db.execute("SELECT id,respuesta FROM eventos_v2 WHERE actividad='E1.01' AND estado='DEMOSTRADO'").fetchone()
    assert json.loads(field[0]) == 32 and field[1] == "SYSTEM_VERIFIED"
    assert field[2] == event[0] and event[1] == literal


def test_v1_se_conserva_y_v2_tiene_excel_propio(private_data):
    alias = "AlumnoDemo"
    catalog, summary = legacy._fuentes()
    first = catalog["campos"][0]
    legacy.procesar({"operacion": "responder", "alumno": alias, "ficha_id": catalog["ficha_id"],
                     "version": catalog["version"], "campo": first["id"],
                     "respuesta_literal": "Leí Cerro Azul en la portada.",
                     "valor_propuesto": summary["project"]["name"]})
    old = private_data / alias / "ficha_individual.sqlite"
    before = old.read_bytes()
    old_excel = private_data / alias / "Ficha_Individual_G01.xlsx"
    before_excel = old_excel.read_bytes()
    state = controller.process({"operacion": "estado", "alumno": alias})
    assert old.read_bytes() == before
    assert old_excel.read_bytes() == before_excel
    assert state["ficha_e1"]["legacy_v1_present"] is True
    new_excel = Path(state["ficha_e1"]["xlsx"])
    assert new_excel.name == "Ficha_Individual_G01_V2.xlsx"
    with zipfile.ZipFile(new_excel) as z:
        assert z.testzip() is None and "xl/workbook.xml" in z.namelist()
        sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert "SYSTEM_VERIFIED" in sheet and "e178b14f" in sheet


def test_v2_reconoce_evidencia_e1_preexistente_sin_duplicar_eventos(private_data):
    alias = "AlumnoDemo"
    base = {"route_id": controller.theory.ROUTE_ID,
            "route_version": controller.theory.VERSION, "alumno": alias}
    controller.theory.procesar({**base, "operacion": "iniciar_etapa", "etapa": "E1"})
    controller.theory.procesar({**base, "operacion": "registrar", "actividad": "E1.01",
                                "estado": "DEMOSTRADO", "tipo_evidencia": "RAZONAMIENTO_PROPIO",
                                "respuesta": "Una muestra aislada solo representa su entorno; faltan datos para extenderla.",
                                "criterio_observado": "Reconoce límite de soporte espacial."})
    db_path = private_data / alias / "teoria_v2.sqlite"
    before = db_path.read_bytes()
    state = controller.process({"operacion": "estado", "alumno": alias})
    assert state["ficha_e1"]["verified_fields"] == 4
    assert state["ficha_e1"]["competencies_demonstrated"] == 1
    assert db_path.read_bytes() == before
