"""Los 26 valores de aplicación tienen una vista estudiantil de la corrida vigente."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kai"))
application = importlib.import_module("aplicacion_g01")
controller = importlib.import_module("recorrido_g01")
VIEW = ROOT / "docs/learning"


def data():
    text = (VIEW / "g01_student_results.js").read_text(encoding="utf-8")
    return json.loads(text.removeprefix("window.PLANMIN_STUDENT_RESULTS=").rstrip(";\n"))


def test_26_observaciones_con_unidad_y_fuente_verificada():
    source, s11, s12 = application.catalog(ROOT)
    view = data()
    assert (view["s11_run_id"], view["s12_run_id"]) == (s11, s12)
    assert [f["id"] for f in view["fields"]] == [f["id"] for f in source]
    assert [f["stage"] for f in view["fields"]].count("S11") == 13
    assert [f["stage"] for f in view["fields"]].count("S12") == 13
    for shown, actual in zip(view["fields"], source):
        assert shown["unit"] == actual["unit"] and shown["label"] == actual["label"]
        assert shown["places"] == actual["places"] and shown["block"] == actual["block"]
        assert shown["value"] == actual["expected"], shown["id"]
    assert len(view["blocks"]) == 19734
    assert len({b[0] for b in view["blocks"]}) == 19734
    example = next(b for b in view["blocks"] if b[0] == view["example_block"])
    columns = {name: i for i, name in enumerate(view["block_columns"])}
    mapped = {"S11.B.CU": "cu_pct_est", "S11.B.RHO": "density_t_m3_est",
              "S11.B.V": "rock_volume_m3", "S11.B.T": "tonnage_t",
              "S11.B.H": "cu_pct_holes", "S11.B.MO": "mo_pct_est",
              "S11.B.AU": "au_gt_est", "S12.B.ALLOC": "allocated_moved_t",
              "S12.B.OPEX": "total_opex_usd"}
    for field in view["fields"]:
        if field["id"] in mapped:
            assert abs(example[columns[mapped[field["id"]]]] - field["value"]) < 1e-6
    s11_csv = ROOT / "outputs/g01_s11" / s11 / "block_model_s11.csv"
    s12_csv = ROOT / "outputs/g01_s12" / s12 / "block_scenario_s12.csv"
    assert view["source_sha256"] == {
        "s11_blocks": hashlib.sha256(s11_csv.read_bytes()).hexdigest(),
        "s12_scenarios": hashlib.sha256(s12_csv.read_bytes()).hexdigest(),
    }


def test_navegacion_kai_y_visores_estudiantiles(tmp_path, monkeypatch):
    monkeypatch.setattr(controller, "DATA", tmp_path)
    monkeypatch.setattr(controller.theory, "DATA", tmp_path)
    pending = controller.process({"operacion": "estado_aplicacion", "alumno": "QA_Consulta"})["pending"]
    assert pending["id"] == "S11.CU75"
    assert pending["tipo_actividad"] == "LECTURA_DE_DATO"
    assert pending["dato_verificado"]["unidad"] == "bloques"
    assert pending["dato_verificado"]["modelo"] == "S11"
    assert pending["consulta_estudiantil"].endswith("#campo-S11.CU75")
    assert (ROOT / pending["consulta_estudiantil"].split("#", 1)[0]).is_file()
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "docs/learning/RESULTADOS_G01.html#s11" in home
    assert "docs/learning/RESULTADOS_G01.html#s12" in home
    assert "docs/learning/VISOR_${stage}_G01.html" in home
    assert "`${folder}/${stage.toLowerCase()}_model_3d.html`" not in home
    student_page = (VIEW / "RESULTADOS_G01.html").read_text(encoding="utf-8")
    assert "g01_student_results.js" in student_page
    assert "consulta_resultados.js" in student_page
    assert 'href="' in student_page
    assert ".json\"" not in student_page and ".csv\"" not in student_page
    for stage in ("S11", "S12"):
        derived = (VIEW / f"VISOR_{stage}_G01.html").read_text(encoding="utf-8")
        original = (ROOT / "outputs" / f"g01_{stage.lower()}" /
                    data()[f"{stage.lower()}_run_id"] / f"{stage.lower()}_model_3d.html").read_text(encoding="utf-8")
        marker = "window.G01_MODEL="
        payload = lambda text: text[text.index(marker):text.index("</script>", text.index(marker))]
        assert payload(derived) == payload(original)
        assert "href=\"block_model_" not in derived
        assert "href=\"s11_summary.json\"" not in derived
        assert "href=\"s12_summary.json\"" not in derived
        assert "visor_estudiantil.js" in derived
