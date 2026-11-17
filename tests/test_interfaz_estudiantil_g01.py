"""La portada conserva resultados y navegación sin exponer operación interna."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = {}
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "section":
            self.current = attributes.get("id")
            self.sections[self.current] = ""
        if tag in {"a", "img", "script"}:
            target = attributes.get("href") or attributes.get("src")
            if target:
                self.links.append(target)

    def handle_endtag(self, tag):
        if tag == "section":
            self.current = None

    def handle_data(self, data):
        if self.current:
            self.sections[self.current] += data


def test_portada_estudiantil_conserva_modelos_y_limites():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    page = Page()
    page.feed(html)
    for section in ("datos", "compositado", "bloques", "s11", "s12", "kai", "estado"):
        assert section in page.sections
    kai = page.sections["kai"].lower()
    assert "kai planeamiento" in kai and "pycharm" in kai and "copilot" in kai
    assert not re.search(r"sqlite|json|\.py\b|controlador|terminal|30 actividades|21 observaciones|prueba automatizada", kai)
    assert "no constituyen una declaración profesional" in page.sections["estado"].lower()
    assert "cu" in page.sections["s11"].lower() or "ley" in page.sections["s11"].lower()
    assert "escenarios a/b" in page.sections["s12"].lower()
    assert "todavía no se dispone" not in (ROOT / "kai/ruta_teoria_v2.json").read_text(encoding="utf-8")


def test_enlaces_estaticos_visibles_resuelven_y_no_son_catalogos():
    page = Page()
    page.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    assert "docs/learning/GUIA_ESTUDIANTE_KAI.html" in page.links
    assert "kai/config_teoria_v2.json" not in page.links
    assert "kai/ficha_individual_g01.json" not in page.links
    assert "data/raw/release_manifest.json" not in page.links
    for target in page.links:
        if target.startswith("#"):
            continue
        assert (ROOT / target.split("#", 1)[0]).is_file(), target
    for target in (
        "outputs/g01_s11/03b42697a864bb6f88e8/s11_model_3d.html",
        "outputs/g01_s12/6a0abc5cdd8fa86ee4a0/s12_model_3d.html",
    ):
        assert (ROOT / target).is_file(), target
    guide = ROOT / "docs/learning/GUIA_ESTUDIANTE_KAI.html"
    guide_page = Page()
    guide_page.feed(guide.read_text(encoding="utf-8"))
    for target in guide_page.links:
        assert (guide.parent / target.split("#", 1)[0]).is_file(), target
