STATUS: PASS

FILES_CHANGED:
- legacy_documenter/models/entry_point.py
- legacy_documenter/models/__init__.py
- legacy_documenter/models/webform.py
- legacy_documenter/extractors/web_event_extractor.py
- legacy_documenter/extractors/webforms_extractor.py
- legacy_documenter/analysis/web_entry_resolver.py
- legacy_documenter/main.py
- tests/test_v1_unittest.py
- codex/V2/V2_R2_RESULTADO.md

TESTS:
- command: python -m unittest discover -s tests
- total: 32
- result: OK
- fixture_validation:
  - command: python main.py tests/fixtures/v2_r1_sample --output output/v2_r2_fixture --verbose
  - result: 3 files, 0 errors
- internal_validation:
  - command: python main.py . --output output/v2_r2_internal --verbose
  - result: 82 files, 0 errors

OUTPUTS:
- output/index/entry_points.json
- output/index/event_bindings.json
- output/index/functional_dependencies.json extended with:
  - WebForm -> Event
  - Event -> Handler
  - Handler -> Method

EVENT_PATTERNS_SUPPORTED:
- VB Handles:
  - Handles btnBuscar.Click
  - Handles Me.Load
  - Handles MyBase.Load
  - Handles btnAceptar.Click, btnGuardar.Click
- Markup:
  - OnClick="handler"
  - OnSelectedIndexChanged="handler"
  - generic On<Event>="handler"
- Lifecycle:
  - Handles Me.Load
  - Handles MyBase.Load
  - Overrides OnInit
  - Overrides OnLoad
  - Overrides OnPreRender

RESOLUTION_RULES:
- confirmed:
  - WebForm has deterministic CodeBehind/CodeFile path.
  - code-behind file has a single compatible class or Inherits matches class.
  - handler method exists exactly once in extracted web event method model.
- unresolved:
  - handler is declared in markup but method cannot be found uniquely.
  - class/code-behind association is not deterministic.
- inferred:
  - not used in V2-R2.
- false_positive_guards:
  - no arbitrary _Click method becomes entry point without Handles or markup On<Event> evidence.
  - JavaScript strings are not event bindings.
  - commented VB handler declarations are ignored by line preprocessing.
- call_graph_connection:
  - confirmed entry points include outgoing_calls from existing V2-R1.1 call index for the handler method.
  - no recursive functional flow traversal is performed.

CORRECTIONS_OR_LIMITATIONS:
- V2-R3 Oracle/SQL/stored-procedure analysis was not implemented.
- Full flow traversal is not implemented; reserved for V2-R4.
- ASP.NET control type resolution is shallow and uses markup tag/control ID only.
- Dynamic event wiring through AddHandler is not implemented.
- Designer/control tree analysis is not implemented.
- Internal validation project has no persistent WebForms entry-point fixture, so R2 functional behavior is covered by unittest fixtures.

REAL_VALIDATION_COMMAND:
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r2_full" --verbose

NEXT:
V2-R2 ready for full real validation.
V2-R3 NOT STARTED.
