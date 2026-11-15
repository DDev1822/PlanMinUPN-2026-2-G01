"""Visor interactivo de M01B G01 con litología preliminar y huecos visibles."""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from src.mod1.desurvey import desurvey
from src.mod1.loader import load_raw_data

ROOT = Path(__file__).resolve().parents[2]


def build(root: Path = ROOT) -> Path:
    source = root / "data/processed/m01b/block_model.csv"
    with source.open(encoding="utf-8", newline="") as stream:
        blocks = list(csv.DictReader(stream))
    if len(blocks) != 19734:
        raise ValueError("M01B G01 incompleto")
    assigned_count = sum(r["lith_status"] == "ASSIGNED" for r in blocks)
    unassigned_rock_count = sum(r["topo_status"] == "ROCK" and r["lith_status"] == "UNASSIGNED" for r in blocks)
    tracks = desurvey(**{k: v for k, v in load_raw_data(root / "data/raw").items() if k in {"collar", "survey"}})
    traces = []
    palette = {"DIO": "#30c4b0", "POR": "#e2b45e", "BRX": "#e37055", "REG": "#8ea9c5"}
    for code, color in palette.items():
        selected = [r for r in blocks if r["lith_status"] == "ASSIGNED" and r["lith_code"] == code]
        traces.append({"type": "scatter3d", "mode": "markers", "name": code,
                       "x": [float(r["x_center"]) for r in selected],
                       "y": [float(r["y_center"]) for r in selected],
                       "z": [float(r["z_center"]) for r in selected],
                       "text": [r["block_id"] for r in selected],
                       "marker": {"size": 3, "color": color, "opacity": .8},
                       "hovertemplate": "%{text}<br>" + code + "<extra></extra>"})
    unknown = [r for r in blocks if r["topo_status"] == "ROCK" and r["lith_status"] == "UNASSIGNED"]
    selected = unknown[::max(1, len(unknown) // 1000)]
    traces.append({"type": "scatter3d", "mode": "markers", "name": "ROCK sin asignar (muestra visual)",
                   "x": [float(r["x_center"]) for r in selected],
                   "y": [float(r["y_center"]) for r in selected],
                   "z": [float(r["z_center"]) for r in selected],
                   "text": [r["block_id"] for r in selected],
                   "marker": {"size": 2, "color": "#65737b", "opacity": .35},
                   "hovertemplate": "%{text}<br>Sin código<extra></extra>"})
    for hole, points in tracks.items():
        traces.append({"type": "scatter3d", "mode": "lines", "name": hole, "showlegend": False,
                       "x": [p["x"] for p in points], "y": [p["y"] for p in points],
                       "z": [p["z"] for p in points], "line": {"color": "#c7d8ec", "width": 2},
                       "hovertemplate": html.escape(hole) + "<extra></extra>"})
    layout = {"paper_bgcolor": "#101719", "plot_bgcolor": "#101719", "font": {"color": "#dce8ed"},
              "scene": {"aspectmode": "data", "xaxis": {"title": "X (m)"},
                        "yaxis": {"title": "Y (m)"}, "zaxis": {"title": "Z (m)"}},
              "margin": {"l": 0, "r": 0, "t": 0, "b": 0}}
    page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>G01 · Modelo geológico preliminar</title><script src="../../assets/plotly-4.1.1.min.js"></script>
<style>body{{background:#101719;color:#dce8ed;font:16px system-ui;margin:1.5rem}}a{{color:#71d6cc}}#plot{{height:75vh}}.note{{color:#a9bec8;max-width:70rem}}</style></head><body>
<h1>G01 · Modelo geológico preliminar</h1><p>DS01/EXP03 · {len(blocks):,} bloques · {assigned_count:,} asignaciones en la reconstrucción local. <a href="../../index.html#bloques">Volver al recorrido</a> · <a href="../../data/processed/m01b/block_model.csv">CSV completo</a></p>
<p class="note">Los puntos representan centros de bloque; las sondas son trayectorias calculadas. La clase ROCK y la litología son preliminares. La nube gris muestra una muestra visual de los {unassigned_rock_count:,} centros ROCK sin asignación. No acredita continuidad geológica ni CRS/datum formal.</p>
<div id="plot" role="img" aria-label="Modelo 3D interactivo de G01"></div><p id="error" role="alert"></p>
<script>const traces={json.dumps(traces,separators=(',',':'))};const layout={json.dumps(layout,separators=(',',':'))};
if(window.Plotly){{Plotly.newPlot('plot',traces,layout,{{responsive:true,displaylogo:false}}).then(()=>window.G01_M01B_READY=true).catch(e=>document.getElementById('error').textContent=String(e));}}
else document.getElementById('error').textContent='Falta Plotly local';</script></body></html>'''
    target = root / "outputs/figures/m01b_g01_3d.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    return target


if __name__ == "__main__":
    print(build())
