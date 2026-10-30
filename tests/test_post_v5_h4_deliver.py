"""Post-V5 H4: final human deliverables (offline HTML package + PDFs) composed from H2 narrative and H3 visuals.

Networkless and deterministic. `deliver` never resolves a provider and never scans or analyzes a source tree.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
import zlib
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from legacy_documenter.deliver import html as H
from legacy_documenter.deliver.markdown import (
    Bullets, Figure, Heading, Para, Quote, Run, Table, parse_inline, parse_markdown, plain, section, walk_runs,
)
from legacy_documenter.deliver.package import (
    DELIVERABLE_IDS, MANIFEST_NAME, PDF_FILES, Builder, DeliveryInvalid, default_visual_scope, generate_delivery, strip_boilerplate,
)
from legacy_documenter.deliver.pdf import PdfDocument, char_width, norm, text_width
from legacy_documenter.main import main as cli_main
from legacy_documenter.orchestration import ai_interpretation
from legacy_documenter.orchestration.ai_only import run_ai_only
from legacy_documenter.review.service import ApprovalService
from legacy_documenter.visuals.package import generate_visuals, load_context
from tests.test_post_v5_h1_ai_only import make_provider
from tests.test_post_v5_h2_audience_docs import H2Base, tree_digest
from tests.test_post_v5_h3_r2_readability import densify


def run_deliver(baseline: Path, out: Path, *extra: str) -> tuple[int, dict]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cli_main(["deliver", str(baseline), "--output", str(out), *extra])
    text = buf.getvalue()
    return code, json.loads(text[text.index("{"):])


class _Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if key in a and a[key] is not None:
                self.refs.append(a[key])
        if "id" in a:
            self.ids.add(a["id"])


def audit_links(pkg: Path) -> tuple[int, list[str]]:
    pages = {p: _Refs() for p in pkg.rglob("*.html")}
    for p, parser in pages.items():
        parser.feed(p.read_text(encoding="utf-8"))
    broken, checked = [], 0
    for p, parser in pages.items():
        for ref in parser.refs:
            if "://" in ref or ref.startswith("mailto:"):
                continue
            path, _, frag = ref.partition("#")
            target = p if not path else (p.parent / path).resolve()
            checked += 1
            if not Path(target).is_file():
                broken.append(f"{p.relative_to(pkg)} -> {ref}")
            elif frag and str(target).endswith(".html"):
                other = pages.get(Path(target)) or pages.get(Path(str(target)))
                if other is not None and frag not in other.ids:
                    broken.append(f"{p.relative_to(pkg)} -> {ref} (fragment)")
    return checked, broken


def page_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    body = raw[raw.index("<main"):raw.index("</main>")]
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()


def pdf_streams(data: bytes) -> list[str]:
    out = []
    for m in re.finditer(rb"stream\n(.*?)\nendstream", data, re.S):
        try:
            out.append(zlib.decompress(m.group(1)).decode("latin-1"))
        except zlib.error:
            pass
    return out


def pdf_text(data: bytes) -> str:
    """Every shown string of every page in order, space separated (tokens are positioned one by one)."""
    out = []
    for stream in pdf_streams(data):
        out += [re.sub(r"\\(.)", r"\1", m) for m in re.findall(r"\((.*?)\) Tj", stream)]
    return " ".join(out)


def pdf_xref_ok(data: bytes) -> bool:
    start = int(re.search(rb"startxref\n(\d+)\n%%EOF\n$", data).group(1))
    table = data[start:].split(b"trailer")[0].decode().split("\n")
    size = int(table[1].split()[1])
    entries = [line for line in table[2:] if line.strip()]
    for number, line in enumerate(entries):
        if number == 0:
            continue
        offset = int(line.split()[0])
        if not data[offset:offset + 20].startswith(f"{number} 0 obj".encode()):
            return False
    return len(entries) == size


# ------------------------------------------------------------------ units
class MarkdownParserTests(unittest.TestCase):
    def test_h2_subset_roundtrip(self):
        md = ("# Título\n\n> Aviso **fuerte** y *énfasis*\n\n## Sección\n\nTexto con `código` y [enlace](a/b.md#x) y \\*literal\\*.\n\n"
              "- uno\n- dos [x](y.md)\n\n| A | B |\n| --- | --- |\n| `a\\|b` | c\\|d |\n| [l](z.md) | `` |\n")
        blocks = parse_markdown(md)
        self.assertEqual([type(b).__name__ for b in blocks], ["Heading", "Quote", "Heading", "Para", "Bullets", "Table"])
        quote = blocks[1].blocks[0].runs
        self.assertTrue(any(r.bold and r.text == "fuerte" for r in quote) and any(r.italic and r.text == "énfasis" for r in quote))
        para = blocks[3].runs
        self.assertTrue(any(r.code and r.text == "código" for r in para))
        self.assertTrue(any(r.href == "a/b.md#x" for r in para))
        self.assertIn("*literal*", plain(para))
        table = blocks[5]
        self.assertEqual(plain(table.rows[0][0]), "a|b")        # `\|` inside a code span is a literal pipe
        self.assertEqual(plain(table.rows[0][1]), "c|d")
        self.assertEqual(plain(table.rows[1][1]), "(nombre vacío en la evidencia)")  # empty evidence name is declared, not drawn as an empty box

    def test_no_markup_leaks_into_text(self):
        runs = parse_inline("**a** *b* `c` [d](e.md) \\<x\\> 100\\% \\_u\\_")
        self.assertEqual(plain(runs), "a b c d <x> 100% _u_")

    def test_section_extracts_by_heading_prefix(self):
        blocks = parse_markdown("# T\n\n## Uno\n\na\n\n## Dos cosas\n\nb\n\n### sub\n\nc\n\n## Tres\n\nd")
        self.assertEqual([plain(b.runs) for b in section(blocks, "Dos") if isinstance(b, (Para, Heading))], ["b", "sub", "c"])
        self.assertEqual(section(blocks, "No existe"), [])

    def test_strip_boilerplate_only_removes_the_generic_notices(self):
        blocks = parse_markdown("# T\n\n> Documentación generada automáticamente a partir del análisis.\n\n> **Cómo leer las etiquetas.** *Confirmado*: x\n\n> Un **área** es una solución.\n")
        kept = strip_boilerplate(blocks)
        self.assertEqual(len(kept), 2)
        self.assertIsInstance(kept[1], Quote)


class HtmlRenderTests(unittest.TestCase):
    def test_text_is_escaped_everywhere(self):
        blocks = [Heading(1, [Run("<script>alert(1)</script>")], "t"), Para([Run('"><img src=x onerror=alert(1)>', bold=True)]),
                  Table([[Run("<b>h</b>")]], [[[Run("a&b <i>", code=True)]]])]
        out = H.render_blocks(blocks, "x/y.html")
        self.assertNotIn("<script>", out)
        self.assertNotIn("<img src=x", out)
        self.assertNotIn("<i>", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertIn("a&amp;b &lt;i&gt;", out)

    def test_status_labels_are_printed_as_text_with_a_pattern_class(self):
        labels = ("Confirmado", "Inferido (regla estructural)", "No resuelto", "Interpretación de IA (no aprobada)", "Canónico (aprobado por una persona)")
        out = H.render_blocks([Table([[Run("Estado")]], [[[Run(label)]] for label in labels])], "p.html")
        for label, cls in (("Confirmado", "confirmed"), ("Inferido (regla estructural)", "inferred"), ("No resuelto", "unresolved"),
                           ("Interpretación de IA (no aprobada)", "ai"), ("Canónico (aprobado por una persona)", "canonical")):
            self.assertIn(f'<span class="st st-{cls}">{label}</span>', out)

    def test_links_are_relative_and_missing_targets_are_plain_text(self):
        out = H.render_blocks([Para([Run("ok", href="functional/areas/x.html#a"), Run("gone", href="nowhere.html", missing=True)])], "technical/modules/m.html")
        self.assertIn('href="../../functional/areas/x.html#a"', out)
        self.assertNotIn('href="nowhere.html"', out)
        self.assertIn("ref-missing", out)

    def test_sections_are_collapsible_but_open(self):
        blocks = [Heading(1, [Run("T")], "t")] + [x for i in range(3) for x in (Heading(2, [Run(f"S{i}")], f"s{i}"), Para([Run("x")]))]
        out = H.render_blocks(blocks, "p.html")
        self.assertEqual(out.count('<details class="sec" open>'), 3)

    def test_long_unbroken_labels_cannot_overflow(self):
        self.assertIn("overflow-wrap:anywhere", H.CSS)
        label = "A" * 600
        out = H.render_blocks([Para([Run(label)])], "p.html")
        self.assertIn(label, out)


class PdfWriterTests(unittest.TestCase):
    def test_metrics_and_transliteration(self):
        self.assertEqual(char_width("i", "F1"), 222)
        self.assertEqual(char_width("é", "F1"), char_width("e", "F1"))
        self.assertEqual(char_width("x", "F4"), 600)
        self.assertEqual(norm("a → b"), "a -> b")
        self.assertGreater(text_width("Hola", "F2", 10), text_width("Hola", "F1", 10))

    def test_structure_is_valid_and_deterministic(self):
        def build() -> tuple[bytes, dict]:
            doc = PdfDocument("Prueba — título largo", row_cap=3)
            doc.reserve_front()
            doc.blocks(parse_markdown("# Uno\n\n## Dos\n\ntexto (con paréntesis) y \\\\ barra\n\n| A | B |\n| --- | --- |\n" +
                                      "\n".join(f"| f{i} | `x{i}` |" for i in range(10)) + "\n"))
            doc.fill_front("Sub", ["meta"])
            return doc.render()
        (a, stats_a), (b, stats_b) = build(), build()
        self.assertEqual(a, b)
        self.assertEqual(stats_a["content_sha256"], stats_b["content_sha256"])
        self.assertTrue(a.startswith(b"%PDF-1.4") and a.rstrip().endswith(b"%%EOF"))
        self.assertTrue(pdf_xref_ok(a))
        self.assertNotIn(b"/CreationDate", a)
        self.assertNotIn(b"/ModDate", a)
        self.assertEqual(stats_a["tables_truncated"], 1)
        self.assertIn("Se muestran 3 de 10 filas", pdf_text(a))
        self.assertIn(b"/Outlines", a)

    def test_long_tokens_and_wide_tables_stay_inside_the_page(self):
        long_token = "Y" * 400
        md = f"# T\n\n{long_token}\n\n| a | b | c | d | e |\n| --- | --- | --- | --- | --- |\n| {long_token} | `{long_token}` | x | y | z |\n"
        doc = PdfDocument("Largo")
        doc.blocks(parse_markdown(md))
        data, _ = doc.render()
        pattern = re.compile(r"/(F\d) ([\d.]+) Tf ([\d.-]+) ([\d.-]+) Td \((.*?)\) Tj")
        seen = 0
        for stream in pdf_streams(data):
            for font, size, x, _y, text in pattern.findall(stream):
                width = text_width(text.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\"), font, float(size))
                self.assertLessEqual(float(x) + width, 595 - 40, text[:20])
                seen += 1
        self.assertGreater(seen, 10)

    def test_figure_without_svg_degrades_to_a_text_note(self):
        doc = PdfDocument("F")
        doc.blocks([Figure("Diagrama X", "visuals/x.svg", "visuals/x.json", "visuals/x.html", "system-map", "S", 3, 2, 800, 400, {"CONFIRMED": 3}, {}, 0)])
        data, stats = doc.render()
        self.assertEqual((stats["figures_drawn"], stats["figures_as_text"]), (0, 1))
        self.assertIn("«visuals/ x. svg»", pdf_text(data))   # the SVG path is named so the reader can open it in the HTML package


class DeliverableSemanticsTests(unittest.TestCase):
    """Deliverable composition with a stub context: no baseline needed."""

    @staticmethod
    def builder(system=None, slots=None, knowledge_run=None, pages=None) -> Builder:
        from legacy_documenter.documentation_v52.categories import KEEP_SIMPLE, Item
        model = SimpleNamespace(system=system or {"name": "S", "areas": 1, "projects": 2, "screens": 3, "flows": 4, "unresolved_flows": 4, "unresolved_share": 100.0},
                                slots={k: [Item({"name": n}, KEEP_SIMPLE, level=2) for n in v] for k, v in (slots or {}).items()})
        info = SimpleNamespace(evidence_manifest_sha256="0" * 64, evidence_schema_version="1", analyzer={}, repository={})
        b = Builder(SimpleNamespace(model=model, source={}), info, Path("."), Path("."), {"diagrams": []}, ("executive", "functional", "technical_overview"),
                    knowledge_run, False)
        b.pages = pages or {}
        return b

    def test_use_cases_are_not_manufactured(self):
        d = self.builder().build_deliverables()["USE_CASES"]
        text = "".join(r.text for r in walk_runs(d["blocks"]))
        self.assertEqual(d["support"], "NO_CONFIRMED_USE_CASES")
        self.assertIn("No hay casos de uso confirmados derivables de la evidencia estática", text)
        for invented in ("Actor:", "Objetivo:", "Precondición", "Flujo principal"):
            self.assertNotIn(invented, text)

    def test_only_recorded_use_case_kinds_are_shown_and_ai_stays_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "proposals").mkdir()
            (run / "knowledge" / "canonical").mkdir(parents=True)
            (run / "knowledge" / "decisions").mkdir()
            proposals = [{"proposal_id": "P1", "proposal_kind": "USE_CASE", "statement": "Registrar solicitud (propuesta)", "evidence_refs": ["E1"]},
                         {"proposal_id": "P2", "proposal_kind": "FLOW_INTERPRETATION", "statement": "Flujo cualquiera", "evidence_refs": ["E2"]},
                         {"proposal_id": "P3", "proposal_kind": "USE_CASE", "statement": "Caso aprobado", "evidence_refs": ["E3"]},
                         {"proposal_id": "P4", "proposal_kind": "USE_CASE", "statement": "Caso rechazado", "evidence_refs": ["E4"]}]
            (run / "proposals" / "AI_PROPOSALS.json").write_text(json.dumps({"proposals": proposals}), encoding="utf-8")
            (run / "knowledge" / "canonical" / "K1.json").write_text(json.dumps(
                {"status": "ACTIVE", "source_proposal_id": "P3", "decision_id": "D1", "content": {"statement": "Caso aprobado", "kind": "USE_CASE"},
                 "evidence_refs": ["E3"]}), encoding="utf-8")
            (run / "knowledge" / "decisions" / "D4.json").write_text(json.dumps({"action": "REJECT", "proposal_id": "P4"}), encoding="utf-8")
            d = self.builder(knowledge_run=run).build_deliverables()["USE_CASES"]
        tables = [b for b in d["blocks"] if isinstance(b, Table)]
        flat = [(plain(r[0]), plain(r[1])) for t in tables for r in t.rows]
        self.assertIn(("Caso aprobado", "Canónico (aprobado por una persona)"), flat)
        self.assertIn(("Registrar solicitud (propuesta)", "Interpretación de IA (no aprobada)"), flat)
        self.assertEqual(len(flat), 2)                       # the non-use-case proposal and the rejected one are not rendered
        self.assertEqual(d["support"], "CANONICAL_ONLY")
        self.assertNotIn(("Registrar solicitud (propuesta)", "Canónico (aprobado por una persona)"), flat)

    def test_external_integrations_do_not_upgrade_unclassified_dependencies(self):
        b = self.builder(system={"name": "S", "unresolved_distinct": 7},
                         slots={"integrations": ["CONN-1"], "platform_libraries": ["System.Web", "System.Xml"], "unclassified_libraries": ["Foo", "Bar", "Baz"]})
        d = b.build_deliverables()["EXTERNAL_INTEGRATIONS"]
        table = next(x for x in d["blocks"] if isinstance(x, Table))
        rows = {plain(r[0]): (plain(r[2]), plain(r[3])) for r in table.rows}
        self.assertEqual(rows["Externa confirmada"], ("1", "Confirmado"))
        self.assertEqual(rows["Plataforma"], ("2", "Inferido (regla estructural)"))
        self.assertEqual(rows["Sin clasificar"], ("3", "No resuelto"))
        self.assertEqual(rows["No resuelto (límites de flujo)"], ("7", "No resuelto"))
        text = "".join(r.text for r in walk_runs(d["blocks"]))
        self.assertIn("no es una integración externa confirmada", text)

    def test_missing_audience_pages_degrade_without_inventing(self):
        built = self.builder().build_deliverables()
        self.assertEqual(set(built), set(DELIVERABLE_IDS))
        self.assertIn("BUSINESS_FLOWS", built)
        self.assertEqual(built["BUSINESS_FLOWS"]["support"], "OBSERVABLE_FLOWS_ONLY")
        self.assertIn(built["FUNCTIONAL_AREAS"]["support"], ("NO_AUDIENCE_SOURCE",))


# ------------------------------------------------------------------ end to end on the fixture
class DeliverFixtureTests(H2Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pkg = cls.tmp / "package"
        with patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")) as guard:
            cls.code, cls.summary = run_deliver(cls.baseline, cls.pkg)
            cls.provider_resolutions = guard.call_count
        cls.manifest = json.loads((cls.pkg / MANIFEST_NAME).read_text(encoding="utf-8"))

    # --- contract / structure
    def test_package_contract_and_manifest(self):
        self.assertEqual((self.code, self.summary["status"]), (0, "SUCCESS"))
        m = self.manifest
        self.assertEqual((m["contract"], m["contract_version"]), ("LegacyMapperDeliverablesManifest", "1.0"))
        for key in ("baseline", "epistemic_legend", "profiles", "deliverables", "visual_package", "pdfs", "provider_calls", "source_scan_invocations",
                    "analyzer_invocations", "files", "counts", "options"):
            self.assertIn(key, m)
        self.assertEqual((m["provider_calls"], m["source_scan_invocations"], m["analyzer_invocations"]), (0, 0, 0))
        self.assertEqual(len(m["baseline"]["evidence_manifest_sha256"]), 64)
        self.assertEqual([s["status"] for s in m["epistemic_legend"]["statuses"]], ["CONFIRMED", "INFERRED", "UNRESOLVED", "AI_INTERPRETATION", "CANONICAL"])
        self.assertEqual({p["audience"] for p in m["profiles"]}, {"executive", "functional", "technical_overview"})
        self.assertNotRegex(json.dumps(m), r"\d{4}-\d{2}-\d{2}T\d{2}:")          # no timestamps
        for rel, info in m["files"].items():
            self.assertFalse(Path(rel).is_absolute())
            data = (self.pkg / rel).read_bytes()
            self.assertEqual((len(data), __import__("hashlib").sha256(data).hexdigest()), (info["bytes"], info["sha256"]), rel)
        self.assertEqual(m["visual_package"]["evidence_manifest_sha256"], m["baseline"]["evidence_manifest_sha256"])
        self.assertEqual(m["counts"]["html_files"], len(list(self.pkg.rglob("*.html"))))

    def test_all_required_deliverable_surfaces_exist(self):
        self.assertEqual(len(DELIVERABLE_IDS), 10)
        for did in ("SYSTEM_OVERVIEW", "MODULE_MAP", "FUNCTIONAL_AREAS", "USE_CASES", "BUSINESS_FLOWS", "ARCHITECTURE_OVERVIEW", "PROJECT_LAYER_MAP",
                    "DATA_INTERACTIONS", "EXTERNAL_INTEGRATIONS", "KNOWN_UNRESOLVED_AREAS"):
            page = self.pkg / "deliverables" / f"{did}.html"
            self.assertTrue(page.is_file(), did)
            self.assertIn("Qué es (y qué no es) esta superficie", page_text(page))
        self.assertEqual([d["id"] for d in self.manifest["deliverables"]], list(DELIVERABLE_IDS))
        self.assertTrue((self.pkg / "deliverables" / "index.html").is_file())

    def test_html_package_navigation_has_no_broken_links(self):
        checked, broken = audit_links(self.pkg)
        self.assertGreater(checked, 100)
        self.assertEqual(broken, [])

    def test_links_are_relative_and_nothing_needs_the_network(self):
        offenders = []
        for path in [*self.pkg.rglob("*.html"), *self.pkg.rglob("*.css"), *self.pkg.rglob("*.js")]:
            text = path.read_text(encoding="utf-8")
            if re.search(r"https?://|//cdn|@import|fetch\(|XMLHttpRequest", text):
                offenders.append(path.name)
        self.assertEqual(offenders, [])
        for path in self.pkg.rglob("*.html"):
            for ref in re.findall(r'(?:href|src)="([^"]*)"', path.read_text(encoding="utf-8")):
                self.assertFalse(ref.startswith(("/", "file:", "\\")), (path.name, ref))
                self.assertNotIn("\\", ref)
            self.assertTrue(path.read_text(encoding="utf-8").startswith("<!doctype html>"))
            self.assertIn('<meta charset="utf-8">', path.read_text(encoding="utf-8"))

    def test_audience_landing_pages_and_shared_navigation(self):
        for audience, needle in (("executive", "Resumen ejecutivo"), ("functional", "Vista funcional"), ("technical", "Vista técnica")):
            page = self.pkg / audience / "index.html"
            text = page_text(page)
            self.assertIn(needle, text)
            self.assertIn("Ruta sugerida para esta audiencia", text)
            self.assertIn("Qué no se sabe", text)
            raw = page.read_text(encoding="utf-8")
            for target in ("index.html", "executive/index.html", "functional/index.html", "technical/index.html", "deliverables/index.html",
                           "deliverables/KNOWN_UNRESOLVED_AREAS.html", "about.html"):
                self.assertIn(f'href="../{target}"', raw)
            self.assertIn('aria-label="Ruta de navegación"', raw)          # breadcrumbs
        self.assertIn("Elija su ruta de lectura", page_text(self.pkg / "index.html"))

    def test_cross_links_system_area_project_flow_data_unresolved(self):
        area = (self.pkg / "functional" / "areas" / "SampleLegacy.html").read_text(encoding="utf-8")
        self.assertIn("Diagramas", area)
        self.assertIn("../../visuals/areas/SampleLegacy/system-map.svg", area)
        self.assertIn('href="../areas.html"', area)
        flows = page_text(self.pkg / "deliverables" / "BUSINESS_FLOWS.html")
        self.assertIn("flujos observables", flows)
        self.assertTrue(list((self.pkg / "visuals" / "flows").glob("*/observable-flow.html")))
        for rel in ("deliverables/DATA_INTERACTIONS.html", "deliverables/KNOWN_UNRESOLVED_AREAS.html"):
            self.assertIn("../visuals/", (self.pkg / rel).read_text(encoding="utf-8"))

    # --- semantics
    def test_use_cases_surface_does_not_invent_content(self):
        text = page_text(self.pkg / "deliverables" / "USE_CASES.html")
        self.assertIn("No hay casos de uso confirmados derivables de la evidencia estática", text)
        self.assertIn("Interacciones observadas", text)
        self.assertIn("flujos observables", text)
        for invented in ("Actor:", "Objetivo:", "Precondición", "caso de uso confirmado:"):
            self.assertNotIn(invented, text)
        self.assertEqual(next(d for d in self.manifest["deliverables"] if d["id"] == "USE_CASES")["support"], "NO_CONFIRMED_USE_CASES")

    def test_business_flows_are_called_observable_flows(self):
        text = page_text(self.pkg / "deliverables" / "BUSINESS_FLOWS.html")
        self.assertIn("No se afirma que representen un flujo de negocio", text)

    def test_external_integrations_keep_four_categories(self):
        text = page_text(self.pkg / "deliverables" / "EXTERNAL_INTEGRATIONS.html")
        for label in ("Externa confirmada", "Plataforma", "Sin clasificar", "No resuelto (límites de flujo)"):
            self.assertIn(label, text)
        self.assertIn("no es una integración externa confirmada", text)

    def test_functional_areas_and_module_map_state_their_grouping_basis(self):
        self.assertIn("No es una función de negocio confirmada", page_text(self.pkg / "deliverables" / "FUNCTIONAL_AREAS.html"))
        module_map = page_text(self.pkg / "deliverables" / "MODULE_MAP.html")
        self.assertIn("solución (área), proyecto y capa inferida", module_map)
        self.assertIn("No se inventan módulos de negocio", module_map)

    def test_statuses_are_preserved_and_never_strengthened(self):
        layers = (self.pkg / "technical" / "layers.html").read_text(encoding="utf-8")
        self.assertIn('class="st st-inferred">Inferido (regla estructural)', layers)
        self.assertNotRegex(layers, r"Inferido[^<]*</span>[^<]*<[^>]*>\s*Confirmado")
        overview = (self.pkg / "executive" / "index.html").read_text(encoding="utf-8")
        self.assertIn('st-confirmed', overview)
        footer = (self.pkg / "index.html").read_text(encoding="utf-8")
        for label in ("Confirmado", "Inferido (regla estructural)", "No resuelto", "Interpretación de IA (no aprobada)", "Canónico (aprobado por una persona)"):
            self.assertIn(label, footer)                                # one shared legend on every page
        about = page_text(self.pkg / "about.html")
        self.assertIn("inferido no se vuelve confirmado", about)
        self.assertIn("lo no resuelto no se lee como ausencia", about)

    def test_unresolved_remains_prominent(self):
        home = (self.pkg / "index.html").read_text(encoding="utf-8")
        self.assertIn("callout-unresolved", home)
        self.assertIn("deliverables/KNOWN_UNRESOLVED_AREAS.html", home)
        page = page_text(self.pkg / "deliverables" / "KNOWN_UNRESOLVED_AREAS.html")
        self.assertIn("Cuánto no se sabe", page)
        self.assertIn("«No resuelto» no significa que falle ni que no exista", page)
        self.assertIn("Señales de lo no resuelto en los diagramas", page)

    def test_visual_assets_resolve_and_keep_their_models(self):
        vm = json.loads((self.pkg / "visuals" / "VISUALS_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(len(vm["diagrams"]), self.manifest["visual_package"]["diagrams"])
        for d in vm["diagrams"]:
            for rel in (d["svg"], d["model"], d["svg"][:-4] + ".html"):
                self.assertTrue((self.pkg / "visuals" / rel).is_file(), rel)
            page = (self.pkg / "visuals" / (d["svg"][:-4] + ".html")).read_text(encoding="utf-8")
            self.assertIn("Nodos (alternativa textual)", page)
            self.assertIn("<img", page)
        for page in self.pkg.rglob("*.html"):
            for src in re.findall(r'<img src="([^"]+)"', page.read_text(encoding="utf-8")):
                self.assertTrue((page.parent / src).resolve().is_file(), (page.name, src))

    def test_search_index_and_script_are_local_and_optional(self):
        index = (self.pkg / "assets" / "search-index.js").read_text(encoding="utf-8")
        self.assertTrue(index.startswith("var LM_SEARCH="))
        data = json.loads(index[len("var LM_SEARCH="):].rstrip(";\n"))
        self.assertIn("deliverables/USE_CASES.html", [row[0] for row in data])
        self.assertGreater(len(list(self.pkg.rglob("*.html"))), 20)       # every page is readable without the script

    # --- PDF
    def test_pdf_documents_are_generated_and_well_formed(self):
        self.assertEqual(sorted(self.manifest["pdfs"]), sorted(f"pdf/{n}" for n in PDF_FILES.values()))
        for rel, info in self.manifest["pdfs"].items():
            data = (self.pkg / rel).read_bytes()
            self.assertTrue(data.startswith(b"%PDF-1.4"), rel)
            self.assertTrue(pdf_xref_ok(data), rel)
            self.assertGreater(info["pages"], 3)
            self.assertEqual(len(info["content_sha256"]), 64)
        overview = (self.pkg / "pdf" / "LegacyMapper_System_Overview.pdf").read_bytes()
        text = "\n".join(pdf_streams(overview))
        for needle in ("Confirmado", "No resuelto", "Resumen del sistema", "Mapa de m", "Estados: CONFIRMADO"):
            self.assertIn(needle, text)
        self.assertEqual(self.manifest["pdfs"]["pdf/LegacyMapper_System_Overview.pdf"]["figures_as_text"], 0)

    def test_pdf_text_never_leaves_the_page(self):
        pattern = re.compile(r"/(F\d) ([\d.]+) Tf ([\d.-]+) ([\d.-]+) Td \((.*?)\) Tj")
        for rel in self.manifest["pdfs"]:
            data = (self.pkg / rel).read_bytes()
            for stream in pdf_streams(data):
                for font, size, x, y, text in pattern.findall(stream):
                    self.assertGreaterEqual(float(x), 0)
                    self.assertGreaterEqual(float(y), 0)
                    width = text_width(text.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\"), font, float(size))
                    self.assertLessEqual(float(x) + width, 842 - 20, (rel, text[:30]))

    # --- determinism / isolation
    def test_rerun_is_byte_identical(self):
        again = self.tmp / "package_again"
        code, _ = run_deliver(self.baseline, again)
        self.assertEqual(code, 0)
        self.assertEqual(tree_digest(again), tree_digest(self.pkg))      # HTML, SVG, JSON, CSS, JS, manifest and PDFs

    def test_consuming_existing_docs_and_visuals_gives_the_same_package(self):
        vis = self.tmp / "vis_for_consume"
        ctx = load_context(self.baseline)
        areas, projects, flows = default_visual_scope(ctx, 10, False)
        generate_visuals(ctx, vis, areas=areas, projects=projects, flows=flows)
        consumed = self.tmp / "package_consumed"
        code, summary = run_deliver(self.baseline, consumed, "--docs-dir", str(self.out), "--visuals-dir", str(vis))
        self.assertEqual((code, summary["status"]), (0, "SUCCESS"))
        a, b = tree_digest(consumed), tree_digest(self.pkg)
        a.pop(MANIFEST_NAME), b.pop(MANIFEST_NAME)
        self.assertEqual(a, b)

    def test_no_provider_scanner_or_analyzer_and_baseline_unchanged(self):
        from legacy_documenter.cli import full_pipeline, pipeline_stages

        def forbidden(*a, **k):
            raise AssertionError("analysis must not run")
        self.assertFalse((self.tmp / "source").exists())
        out = self.tmp / "package_guarded"
        with patch.object(pipeline_stages, "scan_repository", forbidden), patch.object(pipeline_stages, "extract_repository", forbidden), \
                patch.object(pipeline_stages, "resolve_flows", forbidden), patch.object(full_pipeline, "run_full_pipeline", forbidden), \
                patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")) as guard:
            code, summary = run_deliver(self.baseline, out)
        self.assertEqual((code, guard.call_count, summary["provider_calls"], summary["source_scanned"]), (0, 0, 0, False))
        self.assertEqual(self.provider_resolutions, 0)
        self.assertEqual(tree_digest(self.baseline), self.before)

    # --- refusals
    def test_invalid_inputs_are_refused_without_writing(self):
        out = self.tmp / "package_invalid"
        cases = (([str(self.tmp / "missing")], "BASELINE_NOT_FOUND"), ([str(self.baseline), "--include-ai"], "INCLUDE_AI_REQUIRES_AI_RUN"),
                 ([str(self.baseline), "--ai-run", str(self.tmp / "nope")], "AI_RUN_NOT_FOUND"), ([str(self.baseline), "--max-nodes", "2"], "MAX_NODES_TOO_SMALL"))
        for args, reason in cases:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = cli_main(["deliver", *args, "--output", str(out)])
            payload = json.loads(buf.getvalue()[buf.getvalue().index("{"):])
            self.assertEqual((code, payload["status"]), (4, "DELIVER_INPUT_INVALID"))
            self.assertIn(reason, payload["reason"])
        self.assertFalse(out.exists())

    def test_output_must_be_empty_or_a_previous_package_and_never_the_baseline(self):
        with self.assertRaises(DeliveryInvalid) as ctx:
            generate_delivery(self.baseline, self.baseline)
        self.assertEqual(ctx.exception.reason, "DELIVER_OUTPUT_IS_BASELINE")
        foreign = self.tmp / "foreign"
        foreign.mkdir()
        (foreign / "keep.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(DeliveryInvalid) as ctx:
            generate_delivery(self.baseline, foreign)
        self.assertEqual(ctx.exception.reason, "DELIVER_OUTPUT_NOT_EMPTY")
        self.assertTrue((foreign / "keep.txt").is_file())

    def test_stale_visual_package_is_refused(self):
        vis = self.tmp / "vis_stale"
        generate_visuals(load_context(self.baseline), vis, top_areas=1)
        manifest = json.loads((vis / "VISUALS_MANIFEST.json").read_text(encoding="utf-8"))
        manifest["evidence_manifest_sha256"] = "f" * 64
        (vis / "VISUALS_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(DeliveryInvalid) as ctx:
            generate_delivery(self.baseline, self.tmp / "package_stale", visuals_dir=vis)
        self.assertEqual(ctx.exception.reason, "VISUALS_STALE")
        self.assertFalse((self.tmp / "package_stale").exists())

    def test_cli_help_documents_behavior(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            cli_main(["deliver", "--help"])
        text = " ".join(buf.getvalue().split())
        for needle in ("NEVER calls an AI provider", "does NOT rescan", "--docs-dir", "--visuals-dir", "--no-pdf", "--pdf-row-cap", "human_package"):
            self.assertIn(needle, text)

    # --- optional / missing sections
    def test_single_audience_and_no_pdf_leave_a_consistent_package(self):
        out = self.tmp / "package_exec"
        code, summary = run_deliver(self.baseline, out, "--audience", "executive", "--no-pdf")
        self.assertEqual((code, summary["status"], summary["pdf_files"]), (0, "SUCCESS", 0))
        self.assertFalse((out / "functional").exists() or (out / "technical").exists())
        self.assertFalse((out / "pdf").exists())
        checked, broken = audit_links(out)
        self.assertEqual(broken, [])
        nav = (out / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("functional/index.html", nav.split('<div class="layout">')[0])
        self.assertEqual(len(list((out / "deliverables").glob("*.html"))), 11)    # all surfaces still exist (some say "no audience source")
        self.assertIn("No hay casos de uso confirmados", page_text(out / "deliverables" / "USE_CASES.html"))

    def test_rewriting_into_a_previous_package_replaces_it_cleanly(self):
        out = self.tmp / "package_rewrite"
        run_deliver(self.baseline, out)
        stray = out / "executive" / "stale.html"
        stray.write_text("old", encoding="utf-8")
        manifest = json.loads((out / MANIFEST_NAME).read_text(encoding="utf-8"))
        manifest["files"]["executive/stale.html"] = {"sha256": "0", "bytes": 3}
        (out / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
        code, _ = run_deliver(self.baseline, out)
        self.assertEqual(code, 0)
        self.assertFalse(stray.exists())
        self.assertEqual(tree_digest(out), tree_digest(self.pkg))


class AiAndCanonicalPackageTests(H2Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        copy = cls.tmp / "ai_baseline"
        shutil.copytree(cls.baseline, copy)
        cls.ai = run_ai_only(copy, provider=make_provider())
        assert cls.ai.status == "SUCCESS", cls.ai.reason
        cls.ai_dir = cls.ai.ai_run_dir

    def rows_with(self, html: str, needle: str) -> list[str]:
        return [r for r in re.findall(r"<tr>.*?</tr>", html, re.S) if needle in r]

    def test_without_an_ai_run_there_is_no_ai_content(self):
        out = self.tmp / "no_ai"
        code, _ = run_deliver(self.baseline, out)
        self.assertEqual(code, 0)
        for page in out.rglob("*.html"):
            self.assertNotIn("st-ai", page.read_text(encoding="utf-8").split('<footer')[0], page.name)
        self.assertNotIn("IA - NO APROBADA", "".join(p.read_text(encoding="utf-8") for p in out.rglob("*.svg")))

    def test_ai_interpretation_stays_separate_and_is_never_confirmed(self):
        out = self.tmp / "with_ai"
        code, summary = run_deliver(self.baseline, out, "--ai-run", str(self.ai_dir), "--include-ai")
        self.assertEqual((code, summary["status"], summary["provider_calls"]), (0, "SUCCESS", 0))
        interpretation = out / "functional" / "interpretation.html"
        html = interpretation.read_text(encoding="utf-8")
        rows = self.rows_with(html, "Interpretación de IA (no aprobada)")
        self.assertTrue(rows)
        for row in rows:
            self.assertIn("st-ai", row)
            self.assertNotIn("st-confirmed", row)
            self.assertNotIn("st-canonical", row)
        self.assertIn("IA - NO APROBADA", "".join(p.read_text(encoding="utf-8") for p in out.rglob("*.svg")))
        self.assertIsNotNone(re.search(r"No es un hecho|no es un hecho", page_text(interpretation)))
        self.assertEqual(audit_links(out)[1], [])

    def test_canonical_is_labelled_distinctly_after_human_approval(self):
        copy = self.tmp / "ai_run_approved"
        shutil.copytree(self.ai_dir, copy)
        proposal = json.loads((copy / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))["proposals"][0]
        service = ApprovalService(copy)
        service.prepare(proposal["proposal_id"], "Test Reviewer")
        service.decide(proposal["proposal_id"], "APPROVE", "Test Reviewer", rationale="explicit human approval in test")
        out = self.tmp / "with_canonical"
        code, _ = run_deliver(self.baseline, out, "--ai-run", str(copy), "--include-ai")
        self.assertEqual(code, 0)
        html = (out / "functional" / "interpretation.html").read_text(encoding="utf-8")
        rows = self.rows_with(html, "Canónico (aprobado por una persona)")
        self.assertTrue(rows)
        self.assertTrue(all("st-canonical" in r and "st-ai" not in r for r in rows))
        self.assertEqual(self.rows_with(html, "Interpretación de IA (no aprobada)"), [])       # moved from AI to canonical, not duplicated
        self.assertIn("OK CANÓNICO", "".join(p.read_text(encoding="utf-8") for p in out.rglob("*.svg")))


class DecomposedDiagramNavigationTests(H2Base):
    def test_summary_to_detail_links_resolve(self):
        vis = self.tmp / "vis_dense"
        ctx = densify(load_context(self.baseline))
        generate_visuals(ctx, vis, top_areas=3)
        manifest = json.loads((vis / "VISUALS_MANIFEST.json").read_text(encoding="utf-8"))
        details = [d for d in manifest["diagrams"] if d.get("decomposition", {}).get("role") == "detail"]
        self.assertTrue(details)
        out = self.tmp / "package_dense"
        code, summary = run_deliver(self.baseline, out, "--visuals-dir", str(vis), "--no-pdf")
        self.assertEqual((code, summary["status"]), (0, "SUCCESS"))
        self.assertEqual(audit_links(out)[1], [])
        summaries = [d for d in manifest["diagrams"] if d.get("decomposition", {}).get("role") == "summary"]
        page = (out / "visuals" / (summaries[0]["svg"][:-4] + ".html")).read_text(encoding="utf-8")
        self.assertIn("Diagramas de detalle", page)
        child = details[0]
        child_page = (out / "visuals" / (child["svg"][:-4] + ".html")).read_text(encoding="utf-8")
        self.assertIn("Este es un diagrama de detalle. Resumen:", child_page)
        for d in details:
            self.assertTrue((out / "visuals" / d["svg"]).is_file())
        self.assertGreaterEqual(summary["partial_diagrams"], 0)


if __name__ == "__main__":
    unittest.main()
