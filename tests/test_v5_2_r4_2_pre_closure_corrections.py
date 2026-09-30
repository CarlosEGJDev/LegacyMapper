"""V5.2-R4.2: direct tests for `_replace_with_retry` (atomic write retry) and
for the disambiguated "archivos de código" wording of the project document.

Simulates `os.replace` and `time.sleep`: no real waits, fully deterministic."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.documentation_v52.engine import generate_documentation_v52
from legacy_documenter.utils import atomic_write
from legacy_documenter.utils.atomic_write import _REPLACE_RETRY_ATTEMPTS, _replace_with_retry, atomic_write_text
from tests.test_v5_2_r3_3_component_navigation import _source


class ReplaceWithRetryTests(unittest.TestCase):
    def test_transient_permission_error_then_success(self) -> None:
        calls = []

        def flaky(src, dst):
            calls.append((src, dst))
            if len(calls) == 1:
                raise PermissionError("[WinError 5] Access is denied")

        with patch.object(atomic_write.os, "replace", side_effect=flaky), \
                patch.object(atomic_write.time, "sleep") as sleep:
            _replace_with_retry("tmp", Path("dst"))
        self.assertEqual(len(calls), 2)
        sleep.assert_called_once_with(atomic_write._REPLACE_RETRY_INITIAL_DELAY_S)

    def test_all_attempts_fail_then_permission_error_propagates_with_backoff(self) -> None:
        with patch.object(atomic_write.os, "replace", side_effect=PermissionError("denied")) as replace, \
                patch.object(atomic_write.time, "sleep") as sleep:
            with self.assertRaises(PermissionError):
                _replace_with_retry("tmp", Path("dst"))
        self.assertEqual(replace.call_count, _REPLACE_RETRY_ATTEMPTS)
        delays = [c.args[0] for c in sleep.call_args_list]
        self.assertEqual(len(delays), _REPLACE_RETRY_ATTEMPTS - 1)
        self.assertEqual(delays, [atomic_write._REPLACE_RETRY_INITIAL_DELAY_S * 2 ** i for i in range(len(delays))])

    def test_other_exception_is_not_retried(self) -> None:
        with patch.object(atomic_write.os, "replace", side_effect=OSError("disk error")) as replace, \
                patch.object(atomic_write.time, "sleep") as sleep:
            with self.assertRaises(OSError):
                _replace_with_retry("tmp", Path("dst"))
        self.assertEqual(replace.call_count, 1)
        sleep.assert_not_called()

    def test_success_first_try_never_sleeps(self) -> None:
        with patch.object(atomic_write.os, "replace") as replace, patch.object(atomic_write.time, "sleep") as sleep:
            _replace_with_retry("tmp", Path("dst"))
        replace.assert_called_once()
        sleep.assert_not_called()


class AtomicWriteTextRetryIntegrationTests(unittest.TestCase):
    def test_transient_failure_still_writes_content_and_leaves_no_temp(self) -> None:
        real_replace = atomic_write.os.replace
        state = {"n": 0}

        def flaky(src, dst):
            state["n"] += 1
            if state["n"] == 1:
                raise PermissionError("denied")
            return real_replace(src, dst)

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            with patch.object(atomic_write.os, "replace", side_effect=flaky), patch.object(atomic_write.time, "sleep"):
                atomic_write_text(target, "nuevo")
            self.assertEqual(target.read_text(encoding="utf-8"), "nuevo")
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["out.txt"])

    def test_exhausted_retries_remove_temp_and_keep_original(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            target.write_text("original", encoding="utf-8")
            with patch.object(atomic_write.os, "replace", side_effect=PermissionError("denied")), \
                    patch.object(atomic_write.time, "sleep"):
                with self.assertRaises(PermissionError):
                    atomic_write_text(target, "nuevo")
            self.assertEqual(target.read_text(encoding="utf-8"), "original")
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["out.txt"])


class FileCountWordingTests(unittest.TestCase):
    def test_project_text_states_what_each_count_represents(self) -> None:
        path = Path(__file__).resolve().parents[1] / "legacy_documenter" / "documentation_v52" / "defaults" / "i18n" / "es.json"
        text = json.loads(path.read_text(encoding="utf-8"))["dev.module.own_text"]
        self.assertIn("{source_files}", text)
        self.assertIn("compilables", text)
        self.assertIn("archivos de contenido", text)
        self.assertIn("Componentes y archivos", text)

    def test_generated_project_document_renders_clarified_text(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(), out)
            doc = (result.output_dir / "developer" / "modules" / "BLInterfazSAP.md").read_text(encoding="utf-8")
        self.assertIn("archivos de código compilables", doc)
        self.assertIn("archivos de contenido declarados", doc)


if __name__ == "__main__":
    unittest.main()
