TASK: Validate LegacyMapper V2-R3 against full real repository.
DO NOT modify code.
DO NOT start V2-R4.

INPUT:
- output/v2_r3_full/
- output/v2_r2_full/
- codex/V2/V2_R3_RESULTADO.md
- codex/V2/V2_R2_VALIDACION_REAL.md

PRIMARY:
- output/v2_r3_full/index/data_access.json
- output/v2_r3_full/index/stored_procedures.json
- output/v2_r3_full/index/sql_operations.json
- output/v2_r3_full/index/data_parameters.json
- output/v2_r3_full/index/functional_dependencies.json
- output/v2_r3_full/index/calls.json
- output/v2_r3_full/index/entry_points.json
- output/v2_r3_full/index/errors.json

GOAL:
Determine whether V2-R3 persistence mapping is precise and complete enough to authorize V2-R4 functional-flow resolution.

CHECK:

1. METRICS
Report:
- data_access operations total
- confirmed/unresolved
- direct_provider vs wrapper
- operations by type
- OraConn usages
- ExecProc usages
- transaction operations
- stored procedures total/confirmed/unresolved
- unique stored procedures
- SQL operations total
- SELECT/INSERT/UPDATE/DELETE/MERGE counts
- static vs dynamic SQL
- parameters total
- unique parameter names
- Method -> DataAccessOperation edges
- DataAccessOperation -> StoredProcedure edges
- DataAccessOperation -> SQL edges
- DataAccessOperation -> Parameter edges
- duplicate logical edges
- errors

2. ORACLE / WRAPPER COVERAGE
Search repository evidence for representative:
- OracleConnection
- OracleCommand
- OracleDataAdapter
- OracleParameter
- OraConn
- ExecProc
- BeginTrans
- Commit
- Rollback

Compare textual occurrences/patterns against extracted output.

Do not require 100% textual match:
classify gaps as expected, suspicious, or material.

3. DATA ACCESS SAMPLE
Sample >=25 confirmed data-access operations.

Prioritize:
- direct Oracle
- OraConn
- ExecProc
- ExecuteNonQuery
- ExecuteReader
- ExecuteScalar
- DataAdapter.Fill
- transactions
- different projects/modules

Verify:
source file
-> class
-> method
-> typed DB context
-> operation

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Report observed precision estimate.

4. STORED PROCEDURES
Sample >=20 extracted stored procedures.

Verify procedure evidence from source.

Check:
- literal procedure names
- OraConn.ExecProc
- OracleCommand/CommandText
- package.procedure names
- dynamic names remain unresolved
- no fabricated procedure names

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Report unique procedures and major recurring procedures/packages.

5. SQL
Sample >=20 SQL operations if enough exist.

Verify:
- real DB context
- correct SELECT/INSERT/UPDATE/DELETE/MERGE classification
- static/dynamic classification
- no unrelated strings/comments/HTML/JavaScript

Actively search false positives.

6. PARAMETERS
Sample >=20 parameters if enough exist.

Verify where available:
- parameter name
- direction
- DB type
- size
- source expression
- associated operation/procedure

Check that complex/dynamic values are not fabricated.

7. TRANSACTIONS
Validate representative:
BeginTransaction
BeginTrans
Commit
Rollback

Ensure they are associated with actual data-access context.

Check for false Commit/Rollback classifications from unrelated classes.

8. METHOD LINKAGE
Sample >=15:

Method
-> DataAccessOperation
-> StoredProcedure/SQL

Verify containing method/class/project.

Prioritize BL/SYS/DAL projects.

This linkage is CRITICAL for R4.

9. FUTURE FLOW READINESS
Without constructing full flows, verify >=10 cases where existing indexes provide enough evidence for a future chain resembling:

EntryPoint/Handler
-> call graph
-> BL/SYS method
-> DataAccessOperation
-> StoredProcedure/SQL

Do NOT implement or persist these flows.
Only validate whether R4 will have usable endpoints.

10. FALSE POSITIVES
Actively search for:
- unrelated Execute*
- unrelated Fill
- business Commit/Rollback
- SQL words in ordinary strings
- comments
- JavaScript/HTML
- UI/control methods
- OraConn-like names without DB evidence
- duplicate operations
- same source expression emitted multiple times incorrectly

Quantify material findings.

11. FALSE NEGATIVES
Search representative source patterns missed by extractor:
- multiline commands
- variable-assigned CommandText
- dynamic procedure names
- wrapper parameter arrays
- Oracle commands declared as fields
- commands created outside current method
- helper/factory-created connections
- alternative ExecProc signatures

Classify:
NON_BLOCKING
MEDIUM
HIGH
CRITICAL

12. SECURITY
CRITICAL CHECK.

Search generated R3 JSON outputs for possible:
- password
- pwd
- user id
- uid
- credentials
- connection strings containing secrets
- authentication tokens

Verify sanitization.

Any exposed credential/secret => CRITICAL and R3 cannot pass.

Do not reproduce discovered secret values in report.
Report only type/location/status.

13. REGRESSION
Compare R3 against approved R2:

Must preserve:
- calls total/confidence
- confirmed cross-project calls
- entry_points
- event_bindings
- functional dependency dedup
- errors behavior

Report any material regression.

14. SANITY
Report anomalous:
- method with extreme DB-operation count
- procedure receiving implausible number of callers
- huge parameter explosion
- duplicated procedures/operations
- SQL explosion
- unexpected provider/wrapper hotspot

Determine whether plausible or parser defect.

15. DECISION
Return exactly one:

A) V2-R3_APROBADA_PARA_R4
B) V2-R3_REQUIERE_CORRECCIONES
C) V2-R3_NO_CONFIABLE

If B/C:
REQUIRED_FIXES:
CRITICAL
HIGH
MEDIUM
LOW

CRITICAL/HIGH block R4.

Do NOT implement fixes.

OUTPUT:
codex/V2/V2_R3_VALIDACION_REAL.md

FORMAT:
Machine-oriented compact only:

STATUS
METRICS
ORACLE_WRAPPER_COVERAGE
DATA_ACCESS_SAMPLE
STORED_PROCEDURE_SAMPLE
SQL_SAMPLE
PARAMETER_SAMPLE
TRANSACTION_CHECK
METHOD_LINKAGE
FLOW_READINESS
FALSE_POSITIVES
FALSE_NEGATIVES
SECURITY
REGRESSION
SANITY
REQUIRED_FIXES
DECISION

No ZIP.
No additional reports.
No code changes.
V2-R4 NOT STARTED.