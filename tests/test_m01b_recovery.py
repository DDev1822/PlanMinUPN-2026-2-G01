"""Regresión contra los conteos P2–P4 documentados del antecedente G01."""
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reconstructed_g01_m01b_regression():
    qa = json.loads((ROOT / "data/processed/m01b/qa.json").read_text(encoding="utf-8"))
    assert qa["composites"] == 3632
    assert qa["blocks"] == 19734
    assert qa["topography"] == {"ROCK": 12367, "AIR": 5186,
                                "PARTIAL": 1050, "OUTSIDE_TOPO_COVERAGE": 1131}
    assert qa["lithology"] == {"ASSIGNED": 2056, "UNASSIGNED": 10311,
                              "NOT_ELIGIBLE": 7367}
    assert qa["assigned_codes"] == {"DIO": 1029, "POR": 929, "BRX": 89, "REG": 9}
    assert qa["lith_max_xyz_m"] == 26.926
    with (ROOT / "data/processed/m01b/block_model.csv").open(encoding="utf-8", newline="") as stream:
        rows = {r["block_id"]: r for r in csv.DictReader(stream)}
    assert len(rows) == 19734
    assert rows["B014_000_033"]["topo_status"] == "ROCK"
    assert rows["B019_011_034"]["topo_status"] == "AIR"
    assert rows["B007_003_012"]["lith_status"] == "ASSIGNED"
    assert rows["B007_003_012"]["lith_code"] == "DIO"
