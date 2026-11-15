"""Reconstruye P2–P4 G01 con las reglas registradas en ENTREGA_LOCAL_M01B.

La clasificación es preliminar: no existe una verificación formal de CRS/datum.
No altera las observaciones originales de data/raw.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from src.mod1.compositing import build_m01b_composites
from src.mod1.desurvey import desurvey
from src.mod1.loader import load_raw_data
from src.mod1.positioning import position_intervals
from src.mod1.validator import validate_data

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = (242263.825802219, 8196145.039005655, 3067.835482480)
SIZE = (25.0, 25.0, 10.0)
SHAPE = (23, 22, 39)
TOPO_MAX_XY_M = 10.0
# D10 documentó el P25 redondeado a 26,926 m como umbral operativo.
LITH_MAX_XYZ_M = 26.926
TIE_TOL_M = 1e-8


def _write(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _grid() -> list[dict]:
    ox, oy, oz = ORIGIN
    dx, dy, dz = SIZE
    nx, ny, nz = SHAPE
    rows = []
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                x, y, z = ox + i * dx, oy + j * dy, oz + k * dz
                rows.append({"block_id": f"B{i:03d}_{j:03d}_{k:03d}", "i": i, "j": j, "k": k,
                             "x_min": x, "y_min": y, "z_min": z,
                             "x_max": x + dx, "y_max": y + dy, "z_max": z + dz,
                             "x_center": x + dx / 2, "y_center": y + dy / 2, "z_center": z + dz / 2,
                             "dx": dx, "dy": dy, "dz": dz, "volume_m3": dx * dy * dz})
    return rows


def _topography(rows: list[dict], path: Path) -> None:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        points = np.asarray([(float(r["X"]), float(r["Y"]), float(r["Z"]))
                             for r in csv.DictReader(stream)], dtype=float)
    if not np.isfinite(points).all():
        raise ValueError("Topopl contiene coordenadas no finitas")
    tree = cKDTree(points[:, :2])
    centers = np.asarray([(r["x_center"], r["y_center"]) for r in rows])
    dx, dy, _ = SIZE
    offsets = np.asarray([(0., 0.), (-dx / 2, -dy / 2), (-dx / 2, dy / 2),
                          (dx / 2, -dy / 2), (dx / 2, dy / 2)])
    distance, index = tree.query((centers[:, None, :] + offsets[None, :, :]).reshape(-1, 2))
    distance = distance.reshape(len(rows), 5)
    surface_z = points[index, 2].reshape(len(rows), 5)
    for n, row in enumerate(rows):
        supported = bool(np.all(distance[n] <= TOPO_MAX_XY_M))
        floor_below = bool(np.all(row["z_min"] < surface_z[n, 1:]))
        roof_below = bool(np.all(row["z_max"] < surface_z[n, 1:]))
        floor_above = bool(np.all(row["z_min"] > surface_z[n, 1:]))
        roof_above = bool(np.all(row["z_max"] > surface_z[n, 1:]))
        # La novena consulta es el centro 3D; los otros ocho puntos son vértices.
        center_below = row["z_center"] < surface_z[n, 0]
        center_above = row["z_center"] > surface_z[n, 0]
        row["topo_status"] = ("OUTSIDE_TOPO_COVERAGE" if not supported else
                              "ROCK" if floor_below and roof_below and center_below else
                              "AIR" if floor_above and roof_above and center_above else "PARTIAL")
        row["topo_z_m"] = float(surface_z[n, 0]) if distance[n, 0] <= TOPO_MAX_XY_M else ""
        row["topo_center_distance_m"] = float(distance[n, 0])
        row["topo_max_distance_m"] = float(np.max(distance[n]))
        row["topo_supported_queries"] = int(np.count_nonzero(distance[n] <= TOPO_MAX_XY_M)) * 2 - int(distance[n, 0] <= TOPO_MAX_XY_M)


def _lithology(rows: list[dict], raw: dict) -> None:
    trajectory = desurvey(raw["collar"], raw["survey"])
    positioned = position_intervals(trajectory, {"assay": [], "lithology": raw["lithology"],
                                                  "alteration": [], "density": []})["lithology"]
    segments = []
    for row in positioned:
        code = row["lith_code"]
        for md0, md1, xyz0, xyz1 in row["trajectory_segments"]:
            segments.append((np.asarray(xyz0, dtype=float), np.asarray(xyz1, dtype=float), code))
    idx = [n for n, row in enumerate(rows) if row["topo_status"] == "ROCK"]
    centers = np.asarray([[rows[n][axis + "_center"] for axis in "xyz"] for n in idx])
    best = np.full(len(idx), np.inf)
    codes: list[set[str]] = [set() for _ in idx]
    for start, end, code in segments:
        delta = end - start
        denom = float(delta @ delta)
        if denom == 0:
            continue
        projection = np.clip(((centers - start) @ delta) / denom, 0., 1.)
        distances = np.linalg.norm(centers - (start + projection[:, None] * delta), axis=1)
        better = distances < best - TIE_TOL_M
        tied = np.abs(distances - best) <= TIE_TOL_M
        for position in np.flatnonzero(better):
            codes[position] = {code}
        for position in np.flatnonzero(tied & ~better):
            codes[position].add(code)
        best = np.minimum(best, distances)
    for position, n in enumerate(idx):
        row = rows[n]
        row["lith_nearest_distance_m"] = float(best[position])
        if best[position] <= LITH_MAX_XYZ_M and len(codes[position]) == 1:
            row["lith_status"] = "ASSIGNED"
            row["lith_code"] = next(iter(codes[position]))
        else:
            row["lith_status"] = "UNASSIGNED"
            row["lith_code"] = ""
    for row in rows:
        if row["topo_status"] != "ROCK":
            row.update(lith_status="NOT_ELIGIBLE", lith_code="", lith_nearest_distance_m="")


def rebuild(root: Path = ROOT) -> dict:
    raw = load_raw_data(root / "data/raw")
    errors = [f for f in validate_data(raw)["findings"] if f["severity"] == "ERROR"]
    if errors:
        raise ValueError(f"M01 inválido: {errors[:2]}")
    output = root / "data/processed/m01b"
    composites = build_m01b_composites(root / "data/raw", output / "composites.csv")
    rows = _grid()
    _topography(rows, root / "data/raw/Topopl.csv")
    _lithology(rows, raw)
    fields = ("block_id", "i", "j", "k", "x_min", "y_min", "z_min", "x_max", "y_max", "z_max",
              "x_center", "y_center", "z_center", "dx", "dy", "dz", "volume_m3",
              "topo_status", "topo_z_m", "topo_center_distance_m", "topo_max_distance_m",
              "topo_supported_queries", "lith_status", "lith_code", "lith_nearest_distance_m")
    _write(output / "block_model.csv", fields, rows)
    qa = {"group": "G01", "dataset": "DS01", "composites": len(composites), "blocks": len(rows),
          "topography": dict(Counter(r["topo_status"] for r in rows)),
          "lithology": dict(Counter(r["lith_status"] for r in rows)),
          "assigned_codes": dict(Counter(r["lith_code"] for r in rows if r["lith_status"] == "ASSIGNED")),
          "grid_origin_m": ORIGIN, "block_size_m": SIZE, "grid_shape": SHAPE,
          "topo_max_xy_m": TOPO_MAX_XY_M, "lith_max_xyz_m": LITH_MAX_XYZ_M,
          "formal_crs": "UNKNOWN", "method": "nearest_topo_9_queries_and_finite_segment_distance"}
    (output / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    return qa


if __name__ == "__main__":
    print(json.dumps(rebuild(), ensure_ascii=False, indent=2))
