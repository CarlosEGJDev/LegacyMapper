TASK: Validate LegacyMapper V2-R3.1 against full real repository.

DO NOT modify code.
DO NOT start V2-R4.
DO NOT start V2-R5.

BASELINE:
- V2-R2 approved.
- V2-R3 validation: B) V2-R3_REQUIERE_CORRECCIONES.
- V2-R3.1 implemented all requested CRITICAL/HIGH fixes.

INPUT:
- output/v2_r3_1_full/
- output/v2_r3_full/
- output/v2_r2_full/
- codex/V2/V2_R3_VALIDACION_REAL.md
- codex/V2/V2_R3_1_RESULTADO.md

PRIMARY:
- output/v2_r3_1_full/index/data_access.json
- output/v2_r3_1_full/index/stored_procedures.json
- output/v2_r3_1_full/index/sql_operations.json
- output/v2_r3_1_full/index/data_parameters.json
- output/v2_r3_1_full/index/functional_dependencies.json
- output/v2_r3_1_full/index/calls.json
- output/v2_r3_1_full/index/entry_points.json
- output/v2_r3_1_full/index/event_bindings.json
- output/v2_r3_1_full/index/errors.json

GOAL:
Determine whether R3.1 fixed the CRITICAL/HIGH defects from R3 and whether persistence mapping is reliable enough for V2-R4.

==================================================
1. BEFORE/AFTER
==================================================

Compare R3 vs R3.1:

- data_access total/confirmed/unresolved
- repository_wrapper
- direct_provider
- ExecProc
- ExecProcDS
- transaction operations
- stored procedures
- unique stored procedures
- SQL operations by SELECT/INSERT/UPDATE/DELETE/MERGE
- parameters
- parameters with direction
- parameters with db_type
- Method -> DataAccessOperation
- operations with method=null
- operations with class=null
- functional dependency duplicates
- errors

Explain material changes.

Do NOT treat increased counts alone as success.

==================================================
2. CRITICAL-01 SECURITY
==================================================

CRITICAL validation.

Search ALL generated JSON indexes, especially:

- functional_dependencies.json
- data_access.json
- stored_procedures.json
- sql_operations.json
- data_parameters.json

Check nested:
- evidence
- evidence_samples
- expressions
- connection information

Search for possible exposed:
- password
- pwd
- user id
- userid
- uid
- username
- credentials
- token
- connection strings

Distinguish harmless field names from actual secret values.

Do NOT reproduce secret values in report.

Report only:
- file/index
- category
- sanitized/not sanitized
- PASS/FAIL

Any actual exposed credential/secret:
CRITICAL FAIL.

==================================================
3. CRITICAL-02 ORACONN PARAMETERS
==================================================

Validate real repository cases using:

- ByRef x As OraConn
- ByVal x As OraConn
- x As OraConn

Verify operations called through these parameters:

- ExecProc
- ExecProcDS
- BeginTrans
- Commit
- Rollback

Specifically inspect examples around:
- sys/sysCOBMorosidad/CargaMasivaGestion.vb
- sys/sysADHSolicitud/sysSolicSucur.vb
- bl/blSADAdherente/SADCertificados.vb

Verify:

typed OraConn parameter
-> current method
-> DataAccessOperation
-> procedure/transaction

No receiver-global guessing.

Report extracted vs missed representative cases.

==================================================
4. CRITICAL-03 METHOD DETECTION
==================================================

Previous R3 critical issue:
only 442 Method -> DataAccessOperation edges and multiple method=null hotspots.

Recheck hotspots including:
- SADAdh
- blLiqSub
- blMedAdmision
- blADHTraspaso

Search representative methods using:
- Public Shared Function
- Public Shared Sub
- attributes
- multiline declarations
- ByRef/ByVal parameters
- Overrides/Overloads where present

Report:
- Method -> DataAccessOperation edges
- operations method=null
- percentage with method
- before/after R3
- remaining method=null causes

Sample >=20 operations affected by improved method detection.

Classify:
CORRECT
SUSPICIOUS
INCORRECT

CRITICAL acceptance:
method linkage must be materially improved and suitable for R4 traversal.

==================================================
5. EXECPROCDS
==================================================

Previous:
- textual ExecProcDS ~1027
- extracted = 0

Validate R3.1 extraction.

Sample >=15 ExecProcDS operations if available.

Verify:
OraConn receiver
-> containing method
-> ExecProcDS
-> stored procedure
-> parameters where available

Check:
- literal procedure confirmed
- dynamic procedure unresolved
- non-OraConn ExecProcDS ignored

Report coverage gaps.

Do not require 100% grep coverage.

==================================================
6. DIRECT ORACLE + SQL
==================================================

Previous R3:
sql_operations_total=0 despite known SQL evidence.

Validate known example:
- bl/BlIstSIAGF/blUtil.vb

And additional cases if available.

Check:
- OracleCommand
- OracleDataAdapter
- field-level declarations
- CommandText
- Fill
- ExecuteReader
- ExecuteScalar
- ExecuteNonQuery

Validate SQL:
- SELECT
- INSERT
- UPDATE
- DELETE
- MERGE

Sample all if <20, otherwise >=20.

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Verify:
- SQL requires DB context
- dynamic SQL marked dynamic/unresolved as appropriate
- ordinary SQL-like strings ignored
- comments/HTML/JS ignored

SQL=0 is FAIL if known deterministic DB SQL remains undetected.

==================================================
7. PARAMETERS
==================================================

Previous R3:
- parameter names worked
- direction captured=0
- type captured=0

Report R3.1:
- parameters total
- with name
- with direction
- with db_type
- with size
- associated with operation
- associated with stored procedure

Sample >=20 where direction/type exists in source.

Verify exact source evidence.

No guessing based on parameter names.

==================================================
8. STORED PROCEDURES
==================================================

Sample >=25 procedures across:
- ExecProc
- ExecProcDS
- direct Oracle where available
- different projects/modules

Verify:
source
-> method
-> DB operation
-> procedure

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Check:
- package.procedure preserved
- dynamic names not fabricated
- duplicate logical procedures/edges controlled

Report precision estimate.

==================================================
9. TRANSACTIONS
==================================================

Validate representative:
- BeginTrans
- BeginTransaction
- Commit
- Rollback

Include OraConn locals and OraConn method parameters.

Verify transaction operation belongs to actual DB context and containing method.

Search for unrelated Commit/Rollback false positives.

==================================================
10. METHOD LINKAGE / R4 READINESS
==================================================

This is a blocking R4 check.

Validate >=20 chains:

Method
-> DataAccessOperation
-> StoredProcedure/SQL

Then validate >=15 cases where existing indexes provide enough evidence for a future chain:

EntryPoint
-> Handler
-> call graph
-> BL/SYS method
-> DataAccessOperation
-> StoredProcedure/SQL

DO NOT construct/persist R4 flows.

Only prove that R4 has reliable endpoints.

Prioritize cross-project Web -> BL/SYS -> DB examples.

Report:
- usable chains
- broken chains
- cause of broken chains
- readiness assessment

==================================================
11. FALSE POSITIVES
==================================================

Actively search for:
- non-DB ExecProc/ExecProcDS
- unrelated Execute*
- unrelated Fill
- business Commit/Rollback
- ordinary SQL strings
- comments
- JS/HTML
- incorrect method ownership
- incorrect class ownership
- duplicated operations
- same expression emitted repeatedly without justification

Quantify material findings.

==================================================
12. FALSE NEGATIVES
==================================================

Search representative missed patterns:

- OraConn parameters
- OraConn locals
- ExecProc
- ExecProcDS
- multiline arguments
- wrapper arrays
- field-level Oracle objects
- CommandText
- Fill
- ExecuteReader/Scalar/NonQuery
- dynamic procedures
- factory/helper connections

Classify each material gap:

CRITICAL
HIGH
MEDIUM
LOW
NON_BLOCKING

==================================================
13. REGRESSION
==================================================

Compare against approved R2/R1.1.

Must preserve:
- calls total/confidence
- confirmed calls
- cross-project calls
- entry_points
- event_bindings
- existing structural indexes
- dependency dedup
- errors behavior

Any material unrelated regression blocks approval.

==================================================
14. SANITY
==================================================

Check anomalous hotspots:

- operations per method
- method=null hotspots
- procedures per method
- parameters per operation
- transaction explosion
- SQL explosion
- ExecProcDS explosion
- duplicated operations
- unexpected provider classifications

Determine:
PLAUSIBLE
SUSPICIOUS
DEFECT

==================================================
15. DECISION
==================================================

Return exactly one:

A) V2-R3_1_APROBADA_PARA_R4
B) V2-R3_1_REQUIERE_CORRECCIONES
C) V2-R3_1_NO_CONFIABLE

Approval requires:
- security PASS
- OraConn parameter defect fixed
- method linkage materially fixed
- ExecProcDS usable
- direct Oracle/SQL known cases detected
- no CRITICAL/HIGH coverage defect blocking R4
- no material regression
- method -> DB endpoint sufficiently reliable for R4

If B/C:

REQUIRED_FIXES:
CRITICAL
HIGH
MEDIUM
LOW

Only CRITICAL/HIGH block R4 unless evidence demonstrates otherwise.

DO NOT implement fixes.

==================================================
OUTPUT
==================================================

Create only:

codex/V2/V2_R3_1_VALIDACION_REAL.md

FORMAT:

STATUS
BEFORE_AFTER
SECURITY
ORACONN_PARAMETER_VALIDATION
METHOD_DETECTION
EXECPROCDS
DIRECT_ORACLE_SQL
PARAMETERS
STORED_PROCEDURES
TRANSACTIONS
METHOD_LINKAGE
R4_READINESS
FALSE_POSITIVES
FALSE_NEGATIVES
REGRESSION
SANITY
REQUIRED_FIXES
DECISION

Machine-oriented.
Compact.
No ZIP.
No additional reports.
No code changes.
V2-R4 NOT STARTED.