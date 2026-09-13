"""V4.1-R5 -- Risky Orchestrators Characterization: DatabaseExtractor (Target A).

Characterization only. Captures existing behavior of
`legacy_documenter.extractors.database_extractor.DatabaseExtractor` so a later
V4.1-R6 extraction decision has behavioral evidence to work from. No
production code is modified by this round or this test file. Where a
category from the R5 prompt does not exist in current behavior, the test
records NOT_APPLICABLE with evidence rather than inventing behavior.
"""
from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.extractors.database_extractor import DatabaseExtractor

ROOT = Path(__file__).parents[1]


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class PublicSurfaceTests(unittest.TestCase):
    """(1) public construction/import. (2) public signature."""

    def test_construction_and_import(self) -> None:
        extractor = DatabaseExtractor()
        self.assertIsInstance(extractor, DatabaseExtractor)

    def test_extract_signature_pinned(self) -> None:
        sig = str(inspect.signature(DatabaseExtractor.extract))
        self.assertEqual(sig, "(self, path: str | pathlib.Path, root: str | pathlib.Path | None = None) -> dict")

    def test_only_one_public_method(self) -> None:
        public = [name for name, _ in inspect.getmembers(DatabaseExtractor, predicate=inspect.isfunction) if not name.startswith("_")]
        self.assertEqual(public, ["extract"])


class RepresentativeExtractionTests(unittest.TestCase):
    """(3) representative extraction input, across the documented operation kinds."""

    def test_direct_oracle_command_and_stored_procedure(self) -> None:
        # One operation record is emitted per matched *statement* touching the
        # command variable (construction, CommandType assignment, Execute
        # call) -- not one per logical database call. All three carry the
        # same resolved stored_procedure/provider/confidence once the command
        # variable's state is known; deduplication to one logical call is
        # performed downstream (DatabaseResolver), not by this module.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim cmd As New OracleCommand("PKG.SAVE", conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.ExecuteNonQuery()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len(result["operations"]), 3)
            for op in result["operations"]:
                self.assertEqual(op["stored_procedure"], "PKG.SAVE")
                self.assertEqual(op["provider"], "Oracle")
                self.assertEqual(op["operation_kind"], "stored_procedure")
                self.assertEqual(op["confidence"], "confirmed")
            self.assertEqual([op["evidence"][0]["line"] for op in result["operations"]], [3, 4, 5])

    def test_adapter_fill_and_static_sql(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Load()
Dim da As New OracleDataAdapter("SELECT * FROM CLIENTE", conn)
da.Fill(ds)
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertTrue(any(op["operation_kind"] == "fill" and op["sql_operation"] == "SELECT" for op in result["operations"]))

    def test_oraconn_execproc_and_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim dbc As New OraConn()
dbc.BeginTrans()
dbc.ExecProc("PKG.PRC", "P_ID,P_NAME", id, name)
dbc.Commit()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertTrue(any(op["provider"] == "OraConn" and op["stored_procedure"] == "PKG.PRC" for op in result["operations"]))
            self.assertEqual({param["name"] for param in result["parameters"]}, {"P_ID", "P_NAME"})


class EmptyAndMalformedInputTests(unittest.TestCase):
    """(4) empty input. (5) malformed/incomplete input."""

    def test_empty_file_yields_empty_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Empty.vb", "")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(result, {"file": "Empty.vb", "operations": [], "parameters": []})

    def test_no_database_code_yields_empty_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Plain.vb", "Public Class Plain\nPublic Sub Run()\nEnd Sub\nEnd Class")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(result["operations"], [])
            self.assertEqual(result["parameters"], [])

    def test_incomplete_class_without_end_class_does_not_raise(self) -> None:
        # No `End Class`: the parser is line-oriented and never requires balanced
        # block terminators to complete without raising.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Unclosed.vb", """Public Class Repo
Public Sub Save()
Dim cmd As New OracleCommand("PKG.SAVE", conn)
cmd.ExecuteNonQuery()""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len(result["operations"]), 2)

    def test_multiline_continuation_signature_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Sys.vb", """Public Class Sys
<Obsolete()>
Public Shared Sub Crear( _
ByRef dbc As OraConn, _
ByVal idAdm As Integer)
dbc.ExecProc("PSYS.CREAR", "ID_ADM", values, "in", "int")
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            op = next(op for op in result["operations"] if op["stored_procedure"] == "PSYS.CREAR")
            self.assertEqual(op["method"], "Crear")


class ClassificationAndNormalizationTests(unittest.TestCase):
    """(6) database-object classification. (7) normalization."""

    def test_provider_classification_oracle_oledb_and_other(self) -> None:
        extractor = DatabaseExtractor()
        self.assertEqual(extractor._provider("OracleCommand"), "Oracle")
        self.assertEqual(extractor._provider("System.Data.OleDb.OleDbCommand"), "OleDb")
        self.assertEqual(extractor._provider("System.Data.SqlClient.SqlCommand"), "SqlCommand")

    def test_direction_normalization(self) -> None:
        extractor = DatabaseExtractor()
        self.assertEqual(extractor._direction("out"), "Output")
        self.assertEqual(extractor._direction("inout"), "InputOutput")
        self.assertEqual(extractor._direction("return"), "ReturnValue")
        self.assertEqual(extractor._direction("in"), "Input")
        self.assertEqual(extractor._direction("weird"), "weird")

    def test_string_literal_sanitization_redacts_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Run()
Dim conn As New OracleConnection("Data Source=db;User ID=scott;Password=tiger")
Dim cmd As New OracleCommand("PKG.SECRET", conn)
cmd.ExecuteNonQuery()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            for op in result["operations"]:
                for evidence in op["evidence"]:
                    self.assertNotIn("tiger", evidence["expression"])
                    self.assertNotIn("scott", evidence["expression"].lower())


class DeduplicationTests(unittest.TestCase):
    """(8) deduplication -- NOT_APPLICABLE at this module's level."""

    def test_repeated_identical_calls_are_not_deduplicated_here(self) -> None:
        # DatabaseExtractor emits one operation per matched line, in encounter
        # order, with no dedup. Deduplication across the whole repository is
        # performed later by DatabaseResolver (see
        # tests/test_v1_unittest.py::test_v2_r3_1_dedup_and_r1_r2_preserved
        # and ::test_v2_r3_deduplicates_data_access_dependencies_preserving_evidence),
        # not by this module. NOT_APPLICABLE at the DatabaseExtractor level,
        # confirmed by evidence: two identical calls produce two operations.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim cmd As New OracleCommand("PKG.SAVE", conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.ExecuteNonQuery()
cmd.ExecuteNonQuery()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len(result["operations"]), 4)


class OrderingAndIdentifierTests(unittest.TestCase):
    """(9) deterministic ordering. (10) deterministic identifiers."""

    def test_operations_ordered_by_source_encounter_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim cmd As New OracleCommand("PKG.FIRST", conn)
Dim cmd2 As New OracleCommand("PKG.SECOND", conn)
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            names = [op["stored_procedure"] for op in result["operations"] if op["stored_procedure"]]
            self.assertEqual(names, ["PKG.FIRST", "PKG.SECOND"])

    def test_ids_are_not_assigned_by_this_module(self) -> None:
        # `id` is always None on both operations and parameters returned by
        # DatabaseExtractor.extract(); deterministic identifier assignment
        # happens downstream (DatabaseResolver). NOT_APPLICABLE at this
        # module's level for "deterministic identifiers" -- confirmed by
        # evidence rather than assumed.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim cmd As New OracleCommand("PKG.SAVE", conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.ExecuteNonQuery()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertTrue(all(op["id"] is None for op in result["operations"]))


class RepeatedRunEquivalenceTests(unittest.TestCase):
    """(11) repeated-run equivalence."""

    def test_extracting_the_same_file_twice_is_equivalent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim cmd As New OracleCommand("PKG.SAVE", conn)
cmd.ExecuteNonQuery()
End Sub
End Class""")
            first = DatabaseExtractor().extract(vb, root)
            second = DatabaseExtractor().extract(vb, root)
            self.assertEqual(first, second)

    def test_same_instance_reused_across_multiple_files_is_equivalent_to_fresh_instances(self) -> None:
        # main.py constructs one DatabaseExtractor() and calls .extract() in a
        # loop over many files -- confirming instance reuse across calls is
        # safe (no leaked instance state) is the STATE_MODEL evidence this
        # test exists to capture.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb_a = write(root / "A.vb", 'Public Class A\nPublic Sub Save()\nDim cmd As New OracleCommand("PKG.A", conn)\ncmd.ExecuteNonQuery()\nEnd Sub\nEnd Class')
            vb_b = write(root / "B.vb", 'Public Class B\nPublic Sub Save()\nDim cmd As New OracleCommand("PKG.B", conn)\ncmd.ExecuteNonQuery()\nEnd Sub\nEnd Class')
            shared = DatabaseExtractor()
            shared_a, shared_b = shared.extract(vb_a, root), shared.extract(vb_b, root)
            fresh_a, fresh_b = DatabaseExtractor().extract(vb_a, root), DatabaseExtractor().extract(vb_b, root)
            self.assertEqual(shared_a, fresh_a)
            self.assertEqual(shared_b, fresh_b)


class ExceptionBehaviorTests(unittest.TestCase):
    """(12) exception behavior."""

    def test_missing_file_raises_file_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(FileNotFoundError):
                DatabaseExtractor().extract(root / "DoesNotExist.vb", root)

    def test_extract_itself_raises_nothing_for_arbitrary_text(self) -> None:
        # The line-oriented regex parser has no assertion/raise path of its
        # own for malformed VB text; main.py's own try/except around
        # `database_extractor.extract(...)` is defense against unexpected
        # input, not evidence that this module raises on it.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Garbled.vb", "This is not valid VB.NET at all {{{ )) ((")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(result["operations"], [])


class UnresolvedConstructTests(unittest.TestCase):
    """(13) unresolved/unknown constructs."""

    def test_ambiguous_stored_procedure_expression_remains_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save(procName As String)
Dim cmd As New OracleCommand(procName, conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.ExecuteNonQuery()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            unresolved = [op for op in result["operations"] if op["command_type"] == "StoredProcedure" and not op["stored_procedure"]]
            self.assertTrue(unresolved)
            self.assertTrue(all(op["confidence"] == "unresolved" for op in unresolved))

    def test_wrapper_call_on_untyped_variable_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Run()
helper.ExecProc("PKG.BAD")
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(result["operations"], [])


class InstanceStateTests(unittest.TestCase):
    """(14) instance-state behavior -- STATE_MODEL evidence."""

    def test_extract_stores_no_instance_attributes(self) -> None:
        extractor = DatabaseExtractor()
        self.assertEqual(vars(extractor), {})
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", 'Public Class Repo\nPublic Sub Save()\nDim cmd As New OracleCommand("PKG.SAVE", conn)\ncmd.ExecuteNonQuery()\nEnd Sub\nEnd Class')
            extractor.extract(vb, root)
            self.assertEqual(vars(extractor), {})


class NoNetworkOrProviderCallsTests(unittest.TestCase):
    """(15) no network/provider calls."""

    def test_extract_source_has_no_network_or_provider_imports(self) -> None:
        source = inspect.getsource(inspect.getmodule(DatabaseExtractor))
        for token in ("requests", "urllib", "socket", "http.client", "openai", "anthropic"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
