TASK: LegacyMapper V2-R1.1 corrective pass.
INPUT: codex/V2/V2_R1_VALIDACION_REAL.md
DO NOT start V2-R2.

Implement all CRITICAL + HIGH corrections from the validation report:

CRITICAL
1. Filter VB built-ins/intrinsics before Call creation:
IsNothing,CStr,CInt,CDate,CDbl,CDec,IIf,Format,DateAdd,CType,DirectCast,TryCast,GetType and equivalent detected intrinsics.
Do not create inferred local targets for them.

2. Local calls:
Never infer Class.method unless that member exists in the extracted symbol/member model.
Otherwise unresolved/external/builtin as appropriate.

3. Strings:
Do not extract VB calls from string literals, including embedded javascript:*.

HIGH
4. Distinguish method invocation from indexed/default-property access:
Tables(...),Rows(...),Item(...),Attributes(...),Session(...) and equivalent patterns must not become functional method calls unless deterministic evidence proves they are methods.

5. Deduplicate functional_dependencies.json.
Class -> UsesClass must not repeat identical logical relations merely because the same instantiation occurs multiple times.
Preserve evidence without duplicating graph edges where possible.

6. Preserve complete qualifier for fully-qualified calls.
Example:
Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(...)
must retain the full qualifier/receiver path in the structured Call model.

Also implement MEDIUM corrections only when required by the above changes or trivial/safe. Do not expand scope unnecessarily.

TESTS:
- Preserve all V1/V2-R1 tests.
- Add regression tests for every corrected CRITICAL/HIGH defect.
- Include built-ins, strings/javascript, indexed/default properties, deduplication and fully-qualified calls.
- Ambiguous relations must remain unresolved.
- No LLM dependency.

RUN:
python -m unittest discover -s tests

Run fixture/internal validation only.
Do not run the full 14k-file repository unless needed for a targeted verification.

OUTPUT:
codex/V2/V2_R1_1_RESULTADO.md

Report machine-oriented only:
STATUS
FILES_CHANGED
TESTS
CORRECTIONS[ID,status]
KNOWN_LIMITATIONS
REAL_VALIDATION_COMMAND
NEXT

Expected NEXT:
V2-R1.1 ready for full real validation.
V2-R2 NOT STARTED.

Do not create ZIP.
Do not create additional reports.