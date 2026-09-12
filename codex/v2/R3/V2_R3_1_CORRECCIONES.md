# LegacyMapper V2-R3.1 — Correcciones

TASK: Correct V2-R3 based on full real validation.

BASELINE:

* V1 approved.
* V2-R1.1 approved.
* V2-R2 approved.
* V2-R3 implemented.
* V2-R3 real validation decision: B) V2-R3_REQUIERE_CORRECCIONES.

SOURCE OF TRUTH:

* codex/V2/V2_R3_VALIDACION_REAL.md
* codex/V2/V2_R3_RESULTADO.md

DO NOT start V2-R4.
DO NOT implement V2-R5.
DO NOT redesign working R3 components unnecessarily.

## GOAL

Fix all CRITICAL and HIGH defects found in real V2-R3 validation while preserving current precision.

Current validated precision:

* Data-access sample: 25/25 CORRECT.
* Stored-procedure sample: 20/20 CORRECT.
* Material problem is coverage/method linkage/security, not confirmed-operation precision.

Preserve conservative deterministic behavior.

---

## CRITICAL-01 — SANITIZE ALL EXPORTED EVIDENCE

Validation found secret-like connection information surviving in:

`functional_dependencies.json -> evidence / evidence_samples`

Requirement:

Apply sanitization BEFORE any generated evidence is exported.

Must cover at minimum:

* password
* pwd
* user id
* userid
* uid
* username
* credentials
* tokens
* connection-string values

Do not rely only on sanitizing `configuration.json` or R3 primary indexes.

Sanitization must apply to evidence propagated into:

* functional_dependencies.json
* data_access.json
* stored_procedures.json
* sql_operations.json
* data_parameters.json
* any reusable evidence serialization path

Prefer centralized sanitization instead of per-export duplication.

Preserve:

* config key/name
* provider
* structural evidence
* non-secret expression context

Never export secret values.

TESTS REQUIRED:

* connection string with User ID + Password
* Pwd + UID variants
* evidence_samples path
* nested evidence
* no secret survives generated indexes

Any leaked credential = FAIL.

---

## CRITICAL-02 — ORACONN METHOD PARAMETERS

Support methods where OraConn is supplied as a parameter, including:

```vb
ByRef dbc As OraConn
ByVal dbc As OraConn
dbc As OraConn
```

Examples from real validation include patterns in:

* sys/sysCOBMorosidad/CargaMasivaGestion.vb
* sys/sysADHSolicitud/sysSolicSucur.vb
* bl/blSADAdherente/SADCertificados.vb

Requirement:

Method-local data-access context must include typed parameters, not only local variable declarations.

Then recognize calls such as:

```vb
dbc.ExecProc(...)
dbc.ExecProcDS(...)
dbc.BeginTrans(...)
dbc.Commit(...)
dbc.Rollback(...)
```

as belonging to the CURRENT containing method.

Required linkage:

Method
-> DataAccessOperation
-> StoredProcedure/Transaction/etc.

Do not create global receiver-based guesses.

Receiver variable must be deterministically typed as OraConn.

---

## CRITICAL-03 — RESTORE COMPLETE METHOD DETECTION

Real validation found operations with:

`method = null`

Examples/hotspots:

* SADAdh
* blLiqSub
* blMedAdmision
* blADHTraspaso

Fix method extraction/context so R3 recognizes relevant VB.NET declarations including at minimum:

* Public Sub
* Public Function
* Private Sub
* Private Function
* Protected Sub
* Protected Function
* Friend Sub
* Friend Function
* Shared Sub
* Shared Function
* Public Shared Sub
* Public Shared Function
* Protected Shared
* Friend Shared
* Overrides
* Overloads
* MustOverride where applicable
* Async where syntactically relevant
* methods with attributes above declaration
* multiline method signatures
* parameters containing ByRef/ByVal/Optional/ParamArray

Do not break V1 symbol extraction.

R3 may introduce/extend a method-context parser if needed, but reuse existing extraction infrastructure where practical.

Required:

Every R3 operation physically inside a recognized VB method must receive:

* method name
* class when known
* project when known
* source evidence

Do not invent method when source context is ambiguous.

Add regression tests for methods with attributes and multiline signatures.

---

## HIGH-01 — EXECPROCDS

Add deterministic support for:

`OraConn.ExecProcDS(...)`

Real validation found >1000 textual occurrences and zero extracted.

Treat as repository-wrapper data access when receiver is confirmed OraConn.

Extract where deterministically available:

* procedure literal
* wrapper method = ExecProcDS
* parameters
* containing method/class/project
* evidence
* confidence

Stored procedure linkage:

DataAccessOperation
-> StoredProcedure

Do not assume return/business semantics beyond DB access.

Add tests:

* literal procedure
* parameter array
* dynamic procedure expression remains unresolved
* non-OraConn object with ExecProcDS must NOT be classified

---

## HIGH-02 — DIRECT ORACLE FIELD-LEVEL CONTEXT

Support direct Oracle objects declared outside local method scope, such as class fields:

```vb
Private cmd As OracleCommand
Private cnn As OracleConnection
Private da As OracleDataAdapter
```

A method using these confirmed typed fields must inherit their type context.

Support:

* field-level OracleConnection
* OracleCommand
* OracleDataAdapter
* OracleParameter

Do NOT globally propagate fields across unrelated classes.

Resolution scope:
current class only.

---

## HIGH-03 — COMMANDTEXT + FILL / DIRECT SQL

Real validation found real SQL evidence not extracted, including:

`BlIstSIAGF/blUtil.vb`

Patterns to support:

```vb
cmd.CommandText = "SELECT ..."
adapter.Fill(...)
```

and equivalent deterministic variants.

Support CommandText assigned:

* directly as literal
* through a local variable with DB context
* through class field where deterministic

Extract SQL:

* SELECT
* INSERT
* UPDATE
* DELETE
* MERGE

Requirements:

* actual DB command/adapter context required
* static literal -> confirmed/static
* concatenated SQL -> dynamic
* variable expression not deterministically resolved -> unresolved/dynamic
* comments/unrelated strings ignored

Associate when possible:

Method
-> DataAccessOperation
-> SQL

Do not parse arbitrary SQL strings outside DB context.

Add tests for:

* CommandText + Fill
* CommandText + ExecuteReader
* field-level command
* local command
* dynamic concatenation
* unrelated `"SELECT"` string false-positive guard

---

## HIGH-04 — WRAPPER PARAMETER DIRECTION / TYPE

Current validation found parameter names correct but:

* direction captured: 0
* type captured: 0

Extract direction/type when explicitly encoded in repository wrapper arguments.

Examples may include literal enum/constants representing:

* Input
* Output
* InputOutput
* ReturnValue
* OracleDbType/OracleType/etc.

Rules:

* only resolve when literal/enum/member expression is deterministic
* preserve raw expression otherwise
* never guess direction/type by parameter naming convention

Fields:

* name
* direction
* db_type
* size when explicit
* source_expression
* confidence
* evidence

Do not make missing direction/type a failure when source does not provide it.

---

## COVERAGE IMPROVEMENT

After fixes, improve coverage specifically for:

* OraConn typed locals
* OraConn typed parameters
* OraConn class fields if present
* ExecProc
* ExecProcDS
* BeginTrans
* Commit
* Rollback
* direct Oracle commands
* CommandText
* Fill
* ExecuteReader
* ExecuteScalar
* ExecuteNonQuery

Do NOT optimize against raw textual occurrence count.

Textual occurrences include declarations, comments, backups and irrelevant contexts.

Goal is materially better deterministic extraction, not 100% grep coverage.

---

## DO NOT REGRESS CURRENT PRECISION

The following validation quality must be preserved:

* confirmed DataAccessOperation precision
* stored procedure precision
* no fabricated stored procedure names
* no DB classification based only on method name
* zero logical dependency duplicates
* errors do not stop scan

Ambiguous evidence:

* unresolved, or
* omit when DB meaning cannot be established.

Never convert uncertainty into confirmed merely to increase coverage.

---

## METHOD LINKAGE ACCEPTANCE

R4 requires usable method endpoints.

The previous real result had only:

* 442 Method -> DataAccessOperation edges
* 643 extracted stored-procedure operations
* numerous operations with method=None

After corrections:

* material reduction of `method=null`
* ExecProc/ExecProcDS operations inside recognized methods must link to their methods
* method linkage must remain deterministic
* class/project context preserved where V1 ownership permits

Do NOT establish an arbitrary numeric target without source evidence.

Report before/after metrics.

---

## SQL ACCEPTANCE

Previous result:

`sql_operations_total = 0`

while real SQL context exists.

R3.1 must extract at least the known confirmed direct Oracle SQL patterns if they remain present in repository fixtures/internal validation.

Do not force SQL output where no SQL fixture exists.

Add deterministic fixture specifically for SQL.

---

## FUNCTIONAL DEPENDENCIES

Extend/reuse current dependency mechanism.

Required relation types where applicable:

Method -> DataAccessOperation
DataAccessOperation -> StoredProcedure
DataAccessOperation -> SQL
DataAccessOperation -> Parameter
DataAccessOperation -> Connection
Method -> TransactionOperation

Requirements:

* zero duplicate logical edges
* evidence_count preserved
* evidence_samples sanitized
* stable deterministic IDs

---

## TESTS

Preserve ALL existing V1/V2 tests.

Add targeted R3.1 regression tests at minimum:

T01 ByRef OraConn parameter
T02 ByVal OraConn parameter
T03 OraConn parameter ExecProc
T04 OraConn parameter ExecProcDS
T05 OraConn parameter transaction operations
T06 Public Shared Function containing DB operation
T07 Public Shared Sub
T08 method with attribute
T09 multiline method declaration
T10 method with ByRef/ByVal parameters
T11 direct Oracle class field
T12 OracleCommand field used inside method
T13 CommandText SELECT
T14 CommandText dynamic SQL
T15 DataAdapter.Fill
T16 ExecuteReader
T17 ExecProcDS literal stored procedure
T18 ExecProcDS dynamic procedure unresolved
T19 parameter direction extraction
T20 parameter DB type extraction
T21 evidence secret sanitization
T22 functional_dependencies nested evidence sanitization
T23 non-OraConn ExecProcDS false-positive guard
T24 unrelated SQL string false-positive guard
T25 dependency dedup
T26 R1.1 call graph unchanged
T27 R2 entry points unchanged

Add more if needed.

---

## VALIDATION

Run:

```powershell
python -m unittest discover -s tests
```

Then fixture validation.

Then internal repository validation.

DO NOT automatically execute full real repository.

No LLM dependency.

---

## REPORT REQUIRED

Create only:

`codex/V2/V2_R3_1_RESULTADO.md`

FORMAT:

STATUS
FILES_CHANGED
TESTS
CRITICAL_FIXES
HIGH_FIXES
SECURITY
METHOD_DETECTION
ORACONN_PARAMETER_SUPPORT
EXECPROCDS_SUPPORT
DIRECT_ORACLE_SUPPORT
SQL_SUPPORT
PARAMETER_SUPPORT
DEPENDENCY_DEDUP
REGRESSION
KNOWN_LIMITATIONS
REAL_VALIDATION_COMMAND
NEXT

Machine-oriented.
Compact.
No repeated explanations.
No ZIP.
No additional reports.

Include before/after internal metrics where useful.

---

## ACCEPTANCE

PASS only if all are true:

* all previous tests PASS
* new R3.1 tests PASS
* evidence export sanitization PASS
* no known secret survives generated indexes
* OraConn method parameters supported
* ExecProc from OraConn parameter linked to current method
* ExecProcDS supported
* method detection materially improved
* operations inside known methods no longer lose method context due supported declaration patterns
* direct Oracle field-level context supported
* CommandText/Fill real SQL patterns supported
* parameter direction/type captured when deterministic
* stored procedure names never fabricated
* dependency dedup remains 0 logical duplicates
* V2-R1.1 call graph unchanged
* V2-R2 entry points unchanged
* V2-R4 NOT started

---

## REAL VALIDATION COMMAND

After implementation report, recommend:

```powershell
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r3_1_full" --verbose
```

Do not run automatically.

---

## STOP

After implementation + tests:

STOP.

Expected final state:

V2-R3.1 ready for full real validation.
V2-R4 NOT STARTED.
