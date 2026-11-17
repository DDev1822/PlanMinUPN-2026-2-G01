"""Deriva visores 3D estudiantiles sin tocar las generaciones verificadas."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.missions.products import verified_product

DEST = ROOT / "docs/learning"


def swap_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"El visor fuente cambió; esperado una vez: {old[:75]}")
    return text.replace(old, new)


for stage in ("S11", "S12"):
    _, folder, _ = verified_product(ROOT, stage)
    source = folder / f"{stage.lower()}_model_3d.html"
    original = source.read_text(encoding="utf-8")
    text = original.replace("../../../assets/", "../../assets/")
    text = text.replace("../../../index.html", "../../index.html")
    start = text.index('<p><a href="../../index.html#')
    end = text.index('</p>', start) + len('</p>')
    text = text[:start] + (
        f'<p><a href="../../index.html#{stage.lower()}" target="_top">Volver al proyecto</a> · '
        f'<a href="RESULTADOS_G01.html#{stage.lower()}" target="_top">Consultar resultados y bloques</a></p>'
    ) + text[end:]
    start = text.index('<a href="block_scenario_s12.csv"')
    end = text.index('</section>', start)
    text = text[:start] + text[end:]
    text = swap_once(text, 'por ejemplo G01-00000.',
                     'por ejemplo G01-B007_009_017.')
    text = swap_once(text,
        'La porción de roca se integra bajo el TIN y figura en rock_fraction y rock_volume_m3. Gris conserva faltantes.',
        'La porción de roca se integra bajo la superficie topográfica adoptada. Gris conserva los valores sin estimación.')
    text = swap_once(text, f'Corrida <code id="run-id"></code>.',
                     f'Modelo {stage} <code id="run-id"></code>.')
    text = text.replace('G01-ALLOC-01: cada bloque participa proporcionalmente',
                        'Regla de aula: cada bloque participa proporcionalmente', 1)
    text = swap_once(text, '<script src="../../assets/quantitative.js"></script>',
                     '<script src="../../assets/quantitative.js"></script><script src="visor_estudiantil_g01.js"></script>')
    destination = DEST / f"VISOR_{stage}_G01.html"
    destination.write_text(text, encoding="utf-8", newline="\n")
    # El objeto que contiene todos los resultados mineros debe ser idéntico.
    marker = 'window.G01_MODEL='
    payload = lambda s: s[s.index(marker):s.index('</script>', s.index(marker))]
    assert payload(original) == payload(text)
    assert 'href="s11_summary.json"' not in text and 'href="s12_summary.json"' not in text
    assert 'href="block_model_' not in text and 'href="block_scenario_' not in text
    print(stage, source.stat().st_size, destination.stat().st_size,
          hashlib.sha256(payload(text).encode("utf-8")).hexdigest())
