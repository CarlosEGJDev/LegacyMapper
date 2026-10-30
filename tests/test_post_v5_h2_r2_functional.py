"""Post-V5 H2-R2: functional profile readability (action categories, summary-first reading, unresolved explanation).

Presentation-only: the classifier reads the technical operation NAME and never asserts business intent.
"""
from __future__ import annotations

import contextlib
import io
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.documentation_v52.audience import ACTIONS, classify_action, classify_target
from legacy_documenter.orchestration import ai_interpretation
from tests.test_post_v5_h2_audience_docs import FIXTURE, quiet, read, run_docs, tree_digest


def build_variant(tmp: Path, name: str, old: str, new: str) -> tuple[Path, Path]:
    """Deterministic baseline from a fixture copy whose stored-procedure name was renamed (no business meaning added)."""
    source = tmp / f"src_{name}"
    shutil.copytree(FIXTURE, source)
    for path in source.rglob("*"):
        if path.is_file() and path.suffix.lower() in (".vb", ".aspx", ".config"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if old in text:
                path.write_text(text.replace(old, new), encoding="utf-8")
    baseline = tmp / f"base_{name}"
    assert quiet(run_full_pipeline, source, baseline, [], 12).status.value == "SUCCESS"
    shutil.rmtree(source)
    out = tmp / f"docs_{name}"
    code, _ = run_docs(baseline, out)
    assert code == 0
    return baseline, out


class ActionClassifierTests(unittest.TestCase):
    def test_categories_follow_the_documented_vocabulary(self):
        self.assertEqual(ACTIONS, ("read", "create", "update", "delete", "mixed", "unknown"))
        cases = {
            "PPRE_CONTACTOS.GRABA_DIRECCIONES": "create",     # the example of the correction brief
            "PPRE_CONTACTOS.LEE_PERSONA": "read",
            "PPRE_PREVENCION2.TRAER_PERSONA": "read",
            "PPRE_CONSULTAS.BUSCAR_EMPRESAXRUT": "read",
            "PPRE_CONSULTAS.CARGACOMBOCOMUNAS": "read",
            "PADH_SOLICITUD.INSERT_ROW": "create",
            "PPRE_X.CREAR_ENCUESTA": "create",
            "PPRE_CONSULTAS.ACTUALIZAR_ENCUESTA": "update",
            "PPRE_X.MODIFICAR_DATOS": "update",
            "PPRE_CONSULTAS.ELIMINAR_CUESTIONARIO": "delete",
            "PPRE_X.DELETE_ROW": "delete",
            "PPRE_PREVENCION2.GENERARDETALLECERTIFICADO": "unknown",
            "PKG_CUSTOMER.SAVE_CUSTOMER": "unknown",           # ambiguous verb: never guessed
        }
        for name, expected in cases.items():
            self.assertEqual(classify_target(name), expected, name)

    def test_short_tokens_and_look_alikes_are_not_over_matched(self):
        self.assertEqual(classify_target("PPRE_CONTACTOS.LISTADO_X"), "read")        # LISTA prefix
        self.assertEqual(classify_target("PPRE_CONTACTOS.GENERAR"), "unknown")       # CON is exact-only: CONTACTOS is not a read
        self.assertEqual(classify_target("PPRE_CONSULTAS.ACTUALIZAR_ENCUESTA"), "update")  # the package name does not count
        self.assertEqual(classify_target("PKG.ALTAMIRA_SUCURSAL"), "unknown")        # ALTA is exact-only: a place name is not a create
        self.assertEqual(classify_target("PKG.VERIFICAR_X"), "unknown")             # no VER stem

    def test_mixed_and_unknown_are_not_collapsed(self):
        self.assertEqual(classify_target("PKG.BUSCAR_Y_GRABAR"), "mixed")                    # one name, two kinds
        self.assertEqual(classify_action("PKG.TRAER_A, PKG.GRABAR_B"), "mixed")              # two targets, two kinds
        self.assertEqual(classify_action("PKG.TRAER_A, PKG.FOO"), "mixed")                   # a kind plus an unrecognizable target
        self.assertEqual(classify_action("PKG.TRAER_A, PKG.TRAER_B"), "read")                # same kind stays that kind
        self.assertEqual(classify_action("PKG.FOO, PKG.BAR"), "unknown")
        self.assertEqual(classify_action(""), "unknown")
        self.assertEqual(classify_action("PKG.GRABAR_A, PKG.BUSCAR_Y_ELIMINAR"), "mixed")

    def test_classifier_is_deterministic(self):
        for name in ("PKG.TRAER_A, PKG.GRABAR_B", "PKG.LEE_X"):
            self.assertEqual({classify_action(name) for _ in range(5)}, {classify_action(name)})


class FunctionalReadabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="h2r2_"))
        cls.baseline_w, cls.out_w = build_variant(cls.tmp, "write", "SAVE_CUSTOMER", "GRABA_CLIENTE")
        cls.baseline_r, cls.out_r = build_variant(cls.tmp, "read", "SAVE_CUSTOMER", "TRAER_CLIENTE")
        cls.baseline_u, cls.out_u = build_variant(cls.tmp, "unk", "SAVE_CUSTOMER", "PROCESAR_CLIENTE")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def func(self, out: Path, rel: str) -> str:
        return (out / "documentation_v52" / "functional" / rel).read_text(encoding="utf-8")

    def test_area_page_reads_summary_first_not_as_a_raw_trace_inventory(self):
        page = self.func(self.out_w, "areas/SampleLegacy.md")
        headings = re.findall(r"^## (.+)$", page, flags=re.M)
        self.assertEqual(headings[0], "Resumen funcional observable")
        self.assertLess(headings.index("Pantallas con actividad identificada"), headings.index("Interacciones de registro / creación"))
        self.assertLess(headings.index("Interacciones de registro / creación"), headings.index("Trazabilidad técnica"))
        self.assertLess(page.index("Resumen funcional observable"), page.index("GRABA_CLIENTE"))   # explanation before the identifiers
        self.assertIn("Registro / creación", page)

    def test_write_interaction_is_classified_and_traceable(self):
        page = self.func(self.out_w, "areas/SampleLegacy.md")
        self.assertIn("interacción de escritura (registro / creación) detectada", page)
        self.assertIn("`PKG_CUSTOMER.GRABA_CLIENTE`", page)          # original technical identifier kept
        self.assertIn("`Web\\CustomerPage.aspx`", page)               # original screen kept
        self.assertIn("`Click`", page)

    def test_read_variant_uses_read_section_only(self):
        page = self.func(self.out_r, "areas/SampleLegacy.md")
        self.assertIn("Interacciones de consulta", page)
        for absent in ("Interacciones de registro", "Interacciones de modificación", "Interacciones de eliminación", "Operaciones mixtas", "Operaciones no clasificadas"):
            self.assertNotIn(absent, page)                            # empty categories are omitted

    def test_unrecognized_operation_is_not_guessed(self):
        page = self.func(self.out_u, "areas/SampleLegacy.md")
        self.assertIn("Operaciones no clasificadas", page)
        self.assertIn("no puede determinarse", page)
        self.assertNotIn("Interacciones de consulta", page)
        self.assertNotIn("Interacciones de registro", page)

    def test_business_intent_is_never_invented(self):
        text = read(self.out_w, "functional")
        self.assertIn("no determinado por evidencia", text)
        for invented in ("actualiza la dirección", "gestiona contactos", "el usuario guarda", "el usuario actualiza", "gestiona clientes"):
            self.assertNotIn(invented, text.lower())

    def test_global_processes_page_summarizes_before_raw_rows_and_keeps_them_reachable(self):
        page = self.func(self.out_w, "processes.md")
        self.assertLess(page.index("Resumen por tipo de interacción"), page.index("Detalle técnico (trazabilidad)"))
        self.assertLess(page.index("Proyectos con más interacciones"), page.index("Detalle técnico (trazabilidad)"))
        self.assertLess(page.index("Pantallas con más interacciones"), page.index("Detalle técnico (trazabilidad)"))
        self.assertIn("Lo que no se sabe", page)
        self.assertIn("`PKG_CUSTOMER.GRABA_CLIENTE`", page)           # raw rows still reachable below the summary
        self.assertIn("Registro / creación", page)

    def test_readme_leads_with_functional_summary(self):
        readme = self.func(self.out_w, "README.md")
        self.assertLess(readme.index("Resumen funcional observable"), readme.index("## Áreas funcionales"))

    def test_unresolved_explanation_precedes_technical_detail_and_counts_are_kept(self):
        page = self.func(self.out_w, "unresolved.md")
        for before, after in (("Qué significa «no resuelto»", "Detalle técnico (trazabilidad)"), ("Cuánto comportamiento está afectado", "Detalle técnico (trazabilidad)"),
                              ("Por qué el análisis se detiene ahí", "Detalle técnico (trazabilidad)"), ("Qué no debe inferirse", "Detalle técnico (trazabilidad)")):
            self.assertLess(page.index(before), page.index(after))
        self.assertIn("`cmd.ExecuteNonQuery()`", page)                 # technical drill-down kept
        flows = re.search(r"Se detienen ante un límite no resuelto: (\d+)", page)
        self.assertIsNotNone(flows)
        self.assertGreater(int(flows.group(1)), 0)                     # counts are not hidden or reduced
        self.assertIn("Recorridos observados", page)

    def test_executive_and_technical_overview_do_not_gain_functional_vocabulary(self):
        for profile in ("executive", "technical_overview"):
            text = read(self.out_w, profile)
            for functional_only in ("Tipo de interacción", "Consulta / lectura", "Registro / creación", "Interacciones de consulta", "Resumen funcional observable"):
                self.assertNotIn(functional_only, text)
        self.assertEqual(sorted(p.name for p in (self.out_w / "documentation_v52" / "executive").glob("*.md")), ["README.md", "areas.md"])

    def test_rerun_is_byte_identical_and_links_resolve(self):
        again = self.tmp / "docs_again"
        code, _ = run_docs(self.baseline_w, again)
        self.assertEqual(code, 0)
        self.assertEqual(tree_digest(again), tree_digest(self.out_w))
        link = re.compile(r"\]\(([^)#]+)(?:#[^)]*)?\)")
        for md in (self.out_w / "documentation_v52").rglob("*.md"):
            for target in link.findall(md.read_text(encoding="utf-8")):
                if not target.startswith(("http:", "https:")):
                    self.assertTrue((md.parent / target).resolve().exists(), (md.name, target))

    def test_no_provider_and_no_analysis_stage(self):
        from legacy_documenter.cli import full_pipeline, pipeline_stages

        def forbidden(*a, **k):
            raise AssertionError("analysis must not run")
        with patch.object(pipeline_stages, "scan_repository", forbidden), patch.object(pipeline_stages, "extract_repository", forbidden), \
                patch.object(full_pipeline, "run_full_pipeline", forbidden), \
                patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")) as guard:
            code, summary = run_docs(self.baseline_w, self.tmp / "docs_guard")
        self.assertEqual((code, guard.call_count, summary["provider_calls"], summary["source_scanned"]), (0, 0, 0, False))


if __name__ == "__main__":
    unittest.main()
