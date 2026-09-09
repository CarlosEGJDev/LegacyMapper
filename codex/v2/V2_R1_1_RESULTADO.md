STATUS: PASS

FILES_CHANGED:
- legacy_documenter/models/call.py
- legacy_documenter/extractors/call_extractor.py
- legacy_documenter/analysis/call_resolver.py
- tests/test_v1_unittest.py
- codex/V2/V2_R1_1_RESULTADO.md

TESTS:
- command: python -m unittest discover -s tests
- total: 22
- result: OK
- fixture_validation:
  - command: python main.py tests/fixtures/v2_r1_sample --output output/v2_r1_1_fixture --verbose
  - result: 3 files, 0 errors
- internal_validation:
  - command: python main.py . --output output/v2_r1_1_internal --verbose
  - result: 74 files, 0 errors

CORRECTIONS:
- id: CRITICAL-1
  status: DONE
  summary: VB intrinsics/built-ins are filtered before Call creation.
- id: CRITICAL-2
  status: DONE
  summary: Local calls no longer produce inferred Class.method targets unless a member exists in symbols.
- id: CRITICAL-3
  status: DONE
  summary: String literals are stripped from scan text before call extraction, including embedded javascript calls.
- id: HIGH-4
  status: DONE
  summary: Indexed/default-property accessors such as Tables, Rows, Item, Attributes and Session are excluded from functional calls.
- id: HIGH-5
  status: DONE
  summary: functional_dependencies are deduplicated by logical relation and retain evidence_count/evidence_samples.
- id: HIGH-6
  status: DONE
  summary: Fully-qualified calls preserve receiver_path while keeping receiver as the final qualifier segment.

KNOWN_LIMITATIONS:
- Calls without parentheses remain mostly unsupported.
- Overload resolution by signature/argument types is not implemented.
- Imports are extracted but not yet used for full namespace/type disambiguation.
- Framework/external API classification is still limited; many external calls may remain unresolved.
- V2-R2 WebForms event mapping was not started.
- Oracle/SQL/stored procedure mapping was not started.

REAL_VALIDATION_COMMAND:
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r1_1_full" --verbose

NEXT:
V2-R1.1 ready for full real validation.
V2-R2 NOT STARTED.
