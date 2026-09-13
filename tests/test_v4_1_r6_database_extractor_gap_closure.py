"""V4.1-R6 Gate A -- DatabaseExtractor characterization gap closure.

Closes the four DatabaseExtractor gaps R5 left open (see
docs/V4_1/V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION_RESULT.md and
output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json ->
database_extractor.r6_readiness_missing_characterization). No production
code is modified by this file. Freezes existing behavior exactly, including
any quirky-looking but real existing outputs -- this is characterization,
not a bug report.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from legacy_documenter.extractors.database_extractor import DatabaseExtractor

ROOT = Path(__file__).parents[1]


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class Gap1BranchOrderInteractionTests(unittest.TestCase):
    """Gap 1: branch-order interaction between operation-detection regexes.

    Evidence: the six operation-detection branches in extract() (COMMAND_NEW_RE,
    ADAPTER_NEW_RE, COMMAND_TEXT_RE, COMMAND_TYPE_RE, EXECUTE_RE, FILL_RE) each
    end with `continue` in source order -- so at most one of them can fire per
    logical line, and *which one* is entirely determined by textual order in
    extract(), not by any semantic priority. The parameter-detection branches
    (PARAM_ADD_RE, ORACLE_PARAM_RE, DIRECTION_RE) have no `continue` between
    them and so are NOT mutually exclusive: they can all fire for one line.
    """

    def test_command_construction_wins_over_commandtext_on_same_joined_logical_line(self) -> None:
        # VB `:` statement separator keeps both statements on one physical
        # line; both COMMAND_NEW_RE and COMMAND_TEXT_RE textually match this
        # single logical line, but only the first-checked branch
        # (COMMAND_NEW_RE) fires -- the later CommandText assignment
        # ("PKG.OTHER") is completely lost, never appearing anywhere in the
        # output. Reordering the branches in extract() would change which
        # value wins.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", 'Public Class Repo\nPublic Sub Save()\nDim cmd As New OracleCommand("PKG.SAVE", conn) : cmd.CommandText = "PKG.OTHER"\ncmd.ExecuteNonQuery()\nEnd Sub\nEnd Class')
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len(result["operations"]), 2)
            self.assertEqual(result["operations"][0]["command_text"], "PKG.SAVE")
            # "PKG.OTHER" legitimately appears verbatim in the raw evidence
            # expression (the full source line is preserved there), but it
            # never becomes a resolved command_text/stored_procedure value on
            # any operation -- the CommandText assignment itself was never
            # separately detected.
            self.assertFalse(any(op["command_text"] == "PKG.OTHER" or op["stored_procedure"] == "PKG.OTHER" for op in result["operations"]))

    def test_param_add_and_oracle_parameter_both_fire_on_one_line(self) -> None:
        # `cmd.Parameters.Add(New OracleParameter("P_ID", 5))` matches BOTH
        # PARAM_ADD_RE (no `continue`) and ORACLE_PARAM_RE (no `continue`
        # either), so this single line emits TWO parameter records: one via
        # the PARAM_ADD_RE/_parameter path (name unresolved: `_split_args`
        # splits the whole "New OracleParameter(...)" expression as one
        # positional arg, so `_literal` finds no quoted name) and one via the
        # ORACLE_PARAM_RE path (name="P_ID", correctly resolved). This is not
        # deduplicated -- both are frozen exactly as emitted.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", 'Public Class Repo\nPublic Sub Save()\nDim cmd As New OracleCommand("PKG.SAVE", conn)\ncmd.Parameters.Add(New OracleParameter("P_ID", 5))\ncmd.ExecuteNonQuery()\nEnd Sub\nEnd Class')
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len(result["parameters"]), 2)
            self.assertIsNone(result["parameters"][0]["name"])
            self.assertEqual(result["parameters"][0]["confidence"], "unresolved")
            self.assertEqual(result["parameters"][1]["name"], "P_ID")
            self.assertEqual(result["parameters"][1]["confidence"], "confirmed")


class Gap2SplitArgsTests(unittest.TestCase):
    """Gap 2: `_split_args` edge cases, frozen exactly as implemented."""

    def setUp(self) -> None:
        self.extractor = DatabaseExtractor()

    def test_basic_comma_split(self) -> None:
        self.assertEqual(self.extractor._split_args("a, b, c"), ["a", "b", "c"])

    def test_nested_parentheses_are_not_split_on(self) -> None:
        self.assertEqual(self.extractor._split_args("a, (b, c), d"), ["a", "(b, c)", "d"])

    def test_nested_function_call_is_not_split_on(self) -> None:
        self.assertEqual(self.extractor._split_args("f(g(x), y), z"), ["f(g(x), y)", "z"])

    def test_quoted_comma_is_not_split_on(self) -> None:
        self.assertEqual(self.extractor._split_args('"a,b", c'), ['"a,b"', "c"])

    def test_parentheses_inside_quoted_string_are_not_split_on(self) -> None:
        self.assertEqual(self.extractor._split_args('a, "b (c)", d'), ["a", '"b (c)"', "d"])

    def test_doubled_quote_escape_inside_string_preserved(self) -> None:
        self.assertEqual(self.extractor._split_args('"say ""hi, there""", b'), ['"say ""hi, there"""', "b"])

    def test_empty_string_yields_no_parts(self) -> None:
        self.assertEqual(self.extractor._split_args(""), [])

    def test_whitespace_only_yields_one_empty_part(self) -> None:
        # `current` accumulates the whitespace characters (a non-empty list),
        # so the truthiness check at the end appends "".join(current).strip()
        # == "" -- one empty-string part, not zero parts.
        self.assertEqual(self.extractor._split_args("   "), [""])

    def test_empty_argument_between_commas(self) -> None:
        self.assertEqual(self.extractor._split_args("a,,b"), ["a", "", "b"])


class Gap3VariableTypeStateTrackingTests(unittest.TestCase):
    """Gap 3: variable/type-state tracking, isolated from full pipeline runs."""

    def test_use_before_declaration_is_not_recognized(self) -> None:
        # A call on `cmd` appearing before its `Dim` is not recognized as a
        # command call: `variables` does not yet know `cmd`'s type at that
        # point in the single forward pass.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", 'Public Class Repo\nPublic Sub Save()\ncmd.ExecuteNonQuery()\nDim cmd As New OracleCommand("PKG.SAVE", conn)\nEnd Sub\nEnd Class')
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len(result["operations"]), 1)
            self.assertEqual(result["operations"][0]["stored_procedure"], "PKG.SAVE")

    def test_reassignment_overwrites_declared_type_not_merges(self) -> None:
        # `cmd` is declared As OracleCommand, then reassigned to
        # `New OracleDataAdapter(...)`: the tracked type is fully overwritten
        # (last-writer-wins), so a later `.Fill(...)` on the same variable is
        # correctly recognized as an adapter Fill, not a Command call.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", 'Public Class Repo\nPublic Sub Save()\nDim cmd As New OracleCommand("PKG.ONE", conn)\ncmd = New OracleDataAdapter("SELECT 1", conn)\ncmd.Fill(ds)\nEnd Sub\nEnd Class')
            result = DatabaseExtractor().extract(vb, root)
            kinds = [op["operation_kind"] for op in result["operations"]]
            self.assertIn("fill", kinds)
            self.assertTrue(all(op["command_variable"] == "cmd" for op in result["operations"]))

    def test_unknown_undeclared_variable_type_is_silently_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", "Public Class Repo\nPublic Sub Save()\nfoo.ExecuteNonQuery()\nEnd Sub\nEnd Class")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(result["operations"], [])

    def test_variable_scope_lifetime_reset_at_method_boundary(self) -> None:
        # A method-local variable declared in one method is not visible in a
        # sibling method of the same class (only class fields persist across
        # methods).
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", 'Public Class Repo\nPublic Sub First()\nDim cmd As New OracleCommand("PKG.FIRST", conn)\nEnd Sub\nPublic Sub Second()\ncmd.ExecuteNonQuery()\nEnd Sub\nEnd Class')
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len([op for op in result["operations"] if op["method"] == "Second"]), 0)


class Gap4RepeatedVariableNamesAcrossClassesTests(unittest.TestCase):
    """Gap 4: multiple classes reusing the same variable name."""

    def test_same_variable_name_in_two_classes_with_different_types_does_not_cross_contaminate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", (
                'Public Class ClassA\n'
                'Public Sub Save()\n'
                'Dim cmd As New OracleCommand("PKG.A", conn)\n'
                'cmd.ExecuteNonQuery()\n'
                'End Sub\n'
                'End Class\n'
                'Public Class ClassB\n'
                'Public Sub Save()\n'
                'Dim cmd As New OracleDataAdapter("SELECT * FROM B", conn)\n'
                'cmd.Fill(ds)\n'
                'End Sub\n'
                'End Class'
            ))
            result = DatabaseExtractor().extract(vb, root)
            class_a_ops = [op for op in result["operations"] if op["class"] == "ClassA"]
            class_b_ops = [op for op in result["operations"] if op["class"] == "ClassB"]
            self.assertTrue(all(op["stored_procedure"] == "PKG.A" for op in class_a_ops))
            self.assertTrue(all(op["operation_kind"] in {"sql", "fill"} and op["sql_operation"] == "SELECT" for op in class_b_ops))
            # State is class-scoped and reset at each class boundary (END_TYPE_RE
            # clears `variables`/`class_fields`/`commands`/`adapters`), so
            # ClassB's `cmd` never inherits ClassA's OracleCommand typing.
            self.assertFalse(any(op["stored_procedure"] == "PKG.A" for op in class_b_ops))


if __name__ == "__main__":
    unittest.main()
