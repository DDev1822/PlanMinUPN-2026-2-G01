"""El inicio de Kai debe abrir o recuperar la actividad sin tocar modelos."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kai"))
controller = importlib.import_module("recorrido_g01")
theory = controller.theory


@pytest.fixture
def private_data(tmp_path, monkeypatch):
    folder = tmp_path / "students"
    monkeypatch.setattr(controller, "DATA", folder)
    monkeypatch.setattr(theory, "DATA", folder)
    monkeypatch.setattr(controller.e1, "DATA", folder)
    return folder


def test_inicio_sin_alias_pide_solo_pseudonimo(private_data):
    turn = controller.start_turn()
    assert turn["grupo"] == "G01" and turn["proyecto"] == "Cerro Azul"
    assert turn["accion"] == "SOLICITAR_ALIAS"
    assert "alias" in turn["pregunta_principal"].lower()
    assert not private_data.exists()


def test_inicio_e1_no_verifica_modelos_antes_de_ensenar(private_data, monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("E1 no requiere verificar S11/S12")
    monkeypatch.setattr(controller, "product_status", unexpected)
    monkeypatch.setattr(controller.application, "progress", unexpected)
    assert controller.start_turn("AlumnoDemo")["actividad_id"] == "E1.01"


def test_inicio_nuevo_y_retorno_recuperan_actividad(private_data):
    first = controller.start_turn("AlumnoDemo")
    assert first["accion"] == "ENSEÑAR_Y_PREGUNTAR"
    assert first["actividad_id"] == "E1.01"
    assert first["pregunta_principal"] == theory.POR_ID["E1.01"]["pregunta"]
    assert first["explicacion"] == theory.POR_ID["E1.01"]["explicacion"]
    assert first["nuevo"] is True
    assert controller.process({"operacion": "estado", "alumno": "AlumnoDemo"})["etapas"]["E1"] == "E1_EN_CURSO"

    wrong = controller.process({"operacion": "registrar", "alumno": "AlumnoDemo", "actividad": "E1.01",
                                "estado": "REQUIERE_REFUERZO", "respuesta": "Sí, basta un ensayo alto.",
                                "criterio_observado": "Aún extiende una muestra aislada a todo el depósito.",
                                "tipo_evidencia": "ERROR_O_DUDA"})
    assert wrong["actividad_actual"] == "E1.01"
    resumed = controller.start_turn("AlumnoDemo")
    assert resumed["actividad_id"] == "E1.01" and resumed["nuevo"] is False
    assert resumed["eventos"] == 1

    answer = "No aprobaría todo el depósito: una muestra solo representa su ubicación; necesito otras observaciones."
    correct = controller.process({"operacion": "registrar", "alumno": "AlumnoDemo", "actividad": "E1.01",
                                  "estado": "DEMOSTRADO", "respuesta": answer,
                                  "criterio_observado": "Relacionó soporte local con la necesidad de más datos.",
                                  "tipo_evidencia": "RAZONAMIENTO_PROPIO"})
    assert correct["actividad_actual"] == "E1.02"
    later = controller.start_turn("AlumnoDemo")
    assert later["actividad_id"] == "E1.02" and later["eventos"] == 2
    assert controller.start_turn("OtraPersona")["actividad_id"] == "E1.01"
    with pytest.raises(ValueError):
        controller.start_turn("Alias;malicioso")


def test_retorno_recupera_pregunta_pendiente(private_data):
    controller.start_turn("AlumnoDemo")
    controller.process({"operacion": "checkpoint", "alumno": "AlumnoDemo", "actividad": "E1.01",
                        "comprension_parcial": "Ubica el dato en un sondaje.",
                        "pregunta_respondida": "¿Qué muestra el ensayo?",
                        "pregunta_pendiente": "¿Qué faltaría observar antes de extenderlo al depósito?",
                        "dificultad_pendiente": "Confunde dato puntual con modelo.",
                        "proxima_accion": "REFORZAR",
                        "evidencia_estudiante": "El alumno identificó una muestra aislada."})
    turn = controller.start_turn("AlumnoDemo")
    assert turn["actividad_id"] == "E1.01"
    assert turn["pregunta_principal"] == "¿Qué faltaría observar antes de extenderlo al depósito?"


def test_cli_inicio_sin_json(private_data, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["recorrido_g01.py", "inicio", "AlumnoDemo"])
    assert controller.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["actividad_id"] == "E1.01"
    assert output["accion"] == "ENSEÑAR_Y_PREGUNTAR"
