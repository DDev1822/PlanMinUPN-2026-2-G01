"""Genera una vista de consulta desde los productos G01 verificados, sin alterarlos."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kai"))
sys.path.insert(0, str(ROOT))
import aplicacion_g01 as application
from src.missions.products import verified_product

TARGET = ROOT / "docs/learning/g01_student_results.js"
S11_COLUMNS = ["cu_pct_est", "density_t_m3_est", "rock_volume_m3", "tonnage_t",
               "cu_pct_holes", "mo_pct_est", "au_gt_est"]
S12_COLUMNS = ["allocated_moved_t", "total_opex_usd"]
BLOCK_COLUMNS = ["block_id", "i", "j", "k", *S11_COLUMNS, *S12_COLUMNS]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def number(value):
    if value in (None, ""):
        return None
    return float(value)


def build():
    s11_manifest, s11_folder, _ = verified_product(ROOT, "S11")
    s12_manifest, s12_folder, _ = verified_product(ROOT, "S12")
    fields, s11_id, s12_id = application.catalog(ROOT)
    assert len(fields) == 26 and s11_id == s11_manifest["run_id"]
    assert s12_id == s12_manifest["run_id"]
    assert {f["stage"] for f in fields} == {"S11", "S12"}

    s11_path = s11_folder / "block_model_s11.csv"
    s12_path = s12_folder / "block_scenario_s12.csv"
    blocks = {}
    for row in rows(s11_path):
        block_id = row["block_id"]
        assert block_id not in blocks
        blocks[block_id] = [block_id, int(row["i"]), int(row["j"]), int(row["k"]),
                            *(number(row[key]) for key in S11_COLUMNS)]
    relation_a = {}
    for row in rows(s12_path):
        if row["scenario"] != "A":
            continue
        block_id = row["block_id"]
        assert block_id not in relation_a
        relation_a[block_id] = [number(row[key]) for key in S12_COLUMNS]
    assert blocks.keys() == relation_a.keys()
    for block_id, values in blocks.items():
        values.extend(relation_a[block_id])

    example = next(f["block"] for f in fields if f["id"] == "S11.B.CU")
    current = blocks[example]
    index = {key: pos for pos, key in enumerate(BLOCK_COLUMNS)}
    field_to_column = {"S11.B.CU": "cu_pct_est", "S11.B.RHO": "density_t_m3_est",
                       "S11.B.V": "rock_volume_m3", "S11.B.T": "tonnage_t",
                       "S11.B.H": "cu_pct_holes", "S11.B.MO": "mo_pct_est",
                       "S11.B.AU": "au_gt_est", "S12.B.ALLOC": "allocated_moved_t",
                       "S12.B.OPEX": "total_opex_usd"}
    for field in fields:
        if field["id"] not in field_to_column:
            continue
        value = current[index[field_to_column[field["id"]]]]
        assert value is not None and abs(value - float(field["expected"])) < 1e-6, field["id"]

    payload = {
        "group": "G01", "s11_run_id": s11_id, "s12_run_id": s12_id,
        "source_sha256": {
            "s11_blocks": hashlib.sha256(s11_path.read_bytes()).hexdigest(),
            "s12_scenarios": hashlib.sha256(s12_path.read_bytes()).hexdigest(),
        },
        "example_block": example,
        "fields": [{"id": f["id"], "label": f["label"], "unit": f["unit"],
                    "stage": f["stage"], "block": f["block"], "places": f["places"],
                    "value": f["expected"]} for f in fields],
        "block_columns": BLOCK_COLUMNS,
        "blocks": list(blocks.values()),
    }
    TARGET.write_text("window.G01_STUDENT_RESULTS=" + json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n", encoding="utf-8")
    print(json.dumps({"target": str(TARGET), "blocks": len(blocks),
                      "fields": len(fields), "bytes": TARGET.stat().st_size,
                      "s11_run_id": s11_id, "s12_run_id": s12_id}, ensure_ascii=False))


if __name__ == "__main__":
    build()
