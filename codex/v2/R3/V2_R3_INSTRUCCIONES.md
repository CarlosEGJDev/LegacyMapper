# LegacyMapper V2-R3 — Data Access Mapping

TASK: Implement V2-R3.
BASELINE:
- V1 approved.
- V2-R1.1 approved.
- V2-R2 approved.
DO NOT implement V2-R4/R5.

## GOAL

Deterministically map persistence/data-access evidence in legacy VB.NET.

Target:

Method
-> DataAccess API
-> Command/Operation
-> StoredProcedure | SQL
-> Parameters
-> Connection/Configuration

Enable later R4 chains:

WebForm
-> Event
-> Handler
-> BL
-> SYS/DAL
-> Oracle/DB operation

R3 MUST NOT build complete functional flows.

## INPUT

Reuse existing:
- projects
- symbols
- configuration
- dependencies
- calls
- functional_dependencies
- entry_points
- event_bindings
- Evidence/confidence model

Do not duplicate existing V1/R1/R2 resolution.

## R3-01 DATA ACCESS DETECTION

Detect deterministic evidence for common legacy patterns including:

- OracleConnection
- OracleCommand
- OracleDataAdapter
- OracleParameter
- System.Data.OracleClient
- Oracle.DataAccess
- CommandText
- CommandType
- CommandType.StoredProcedure
- ExecuteNonQuery
- ExecuteReader
- ExecuteScalar
- Fill

Also support repository-specific wrappers when evidence exists, including observed legacy patterns such as:

- OraConn
- ExecProc
- BeginTrans
- Commit
- Rollback
- Close

Wrapper names alone must NOT prove Oracle/database semantics.
Require contextual evidence.

Architecture must permit additional providers/wrappers later.

## R3-02 CONNECTIONS

Extract where deterministically available:

- connection variable
- connection type/provider
- connection-string key/name
- configuration source
- referenced provider/assembly
- containing method/class/project

NEVER export:
- passwords
- credentials
- secret connection-string values

Reuse V1 sanitization.

## R3-03 COMMAND MODEL

Create structured data-access operation model.

Minimum:

{
  "id": "...",
  "operation_kind": "...",
  "provider": "...",
  "command_variable": "...",
  "command_type": "...",
  "command_text": "...",
  "stored_procedure": "...",
  "sql_operation": "...",
  "connection": "...",
  "class": "...",
  "method": "...",
  "project": "...",
  "confidence": "...",
  "evidence": [...]
}

Stable deterministic IDs.

Allowed confidence:
- confirmed
- unresolved

Avoid inferred unless deterministic rules justify it.

## R3-04 STORED PROCEDURES

Detect stored procedure usage when supported by evidence such as:

- CommandType.StoredProcedure
- CommandText assignment
- OracleCommand construction
- wrapper ExecProc(...)
- equivalent deterministic patterns

Extract when possible:

- package
- procedure
- raw expression
- resolved literal name
- containing method/class/project
- evidence

If procedure name is dynamically constructed:
- preserve expression
- stored_procedure = unresolved
- do NOT fabricate value.

## R3-05 SQL

Detect SQL statements:

- SELECT
- INSERT
- UPDATE
- DELETE
- MERGE

Only from actual VB expressions/string assignments associated with data-access context.

Do NOT interpret:
- comments
- JavaScript
- HTML
- unrelated strings containing SQL words

Store:
- operation type
- sanitized/normalized statement or evidence
- dynamic/static status
- containing method/class/project

Do not execute SQL.

## R3-06 PARAMETERS

Detect parameters associated with commands/procedures.

Support relevant patterns:

- OracleParameter
- Parameters.Add
- Parameters.AddWithValue where applicable
- parameter collections
- wrapper parameter arrays when deterministically recognizable

Extract when available:

- name
- direction
- Oracle/DB type
- size
- source expression
- literal/non-literal
- associated command/procedure
- evidence

Do NOT evaluate arbitrary expressions.

Do NOT expose secrets.

## R3-07 WRAPPER ANALYSIS

Legacy repository uses wrappers such as OraConn/ExecProc.

Map wrappers conservatively.

Example pattern:

Dim dbc As OraConn
...
dbc.ExecProc(...)

Extract as data-access operation only when OraConn/database semantics are supported by repository evidence.

Preserve:
- wrapper type
- method
- arguments
- containing application method
- evidence

Do not require wrapper source code to exist if provider/DLL/config evidence establishes external data-access role.

Classification should distinguish:

- direct_provider
- repository_wrapper
- external_wrapper
- unresolved

## R3-08 TRANSACTIONS

Detect transaction operations when deterministically associated with data access:

- BeginTransaction
- BeginTrans
- Commit
- Rollback

Represent separately from stored procedure/SQL execution.

Do not interpret business semantics.

## R3-09 DATA ACCESS DEPENDENCIES

Extend functional dependencies with normalized relations as applicable:

Method -> DataAccessOperation
DataAccessOperation -> StoredProcedure
DataAccessOperation -> SQL
DataAccessOperation -> Connection
DataAccessOperation -> Parameter
Method -> TransactionOperation

Deduplicate using approved R1.1 mechanism.

Preserve:
- confidence
- evidence_count
- evidence_samples

## R3-10 CALL GRAPH LINK

Connect R3 operations to existing containing methods.

Required:

Method
-> DataAccessOperation

This allows R4 later to traverse:

EntryPoint
-> Handler
-> Calls
-> Method
-> DataAccessOperation

DO NOT perform recursive flow traversal in R3.

## OUTPUT

Add:

output/index/data_access.json
output/index/stored_procedures.json
output/index/sql_operations.json
output/index/data_parameters.json

Extend:

output/index/functional_dependencies.json

Optional separate transaction index only if structurally justified.

Do not break/remove existing indexes.

## FALSE POSITIVE GUARDS

Must NOT classify as DB operation solely because text contains:

- Execute
- Fill
- Commit
- Close
- Connection
- Command
- Select
- Update
- Delete
- Insert

Require data-access context.

Exclude:

- comments
- JavaScript
- HTML
- unrelated strings
- collection access
- UI controls
- similarly named business methods

Ambiguous -> unresolved or omit when no meaningful DB evidence exists.

## SECURITY

CRITICAL:

Never output:
- passwords
- credentials
- authentication tokens
- secret connection-string values

Connection strings must be sanitized.

Prefer configuration key/name/provider over raw value.

Tests must verify sanitization.

## TESTS

Preserve ALL V1/R1/R2 tests.

Add regression tests covering at least:

T01 OracleConnection
T02 OracleCommand
T03 CommandType.StoredProcedure
T04 CommandText stored procedure
T05 ExecuteNonQuery/Reader/Scalar
T06 OracleDataAdapter.Fill
T07 OracleParameter extraction
T08 parameter direction/type
T09 static SELECT
T10 INSERT/UPDATE/DELETE/MERGE
T11 dynamic SQL expression -> unresolved/dynamic
T12 OraConn + ExecProc
T13 BeginTrans/Commit/Rollback
T14 method -> data operation
T15 operation -> stored procedure
T16 connection/config linkage
T17 secret sanitization
T18 comments/string false-positive guard
T19 unrelated Execute/Fill not DB
T20 functional dependency dedup
T21 ambiguous procedure expression remains unresolved
T22 existing R2 entry points/calls unaffected

## VALIDATION

Run:

python -m unittest discover -s tests

Run fixture/internal validation.

Do NOT automatically execute full 14k-file repository.

No LLM dependency.

## ACCEPTANCE

PASS only if:

- all previous tests remain PASS;
- R3 tests PASS;
- direct Oracle access is detected;
- legacy wrappers are conservatively detected;
- stored procedures can be extracted when evidenced;
- SQL operations detected with DB context;
- parameters linked where possible;
- transaction operations detected;
- method -> data access linkage exists;
- dynamic values are not fabricated;
- secrets remain sanitized;
- functional dependencies remain deduplicated;
- V2-R1.1 call graph unchanged;
- V2-R2 entry points unchanged;
- errors in individual files do not stop scan;
- R4/R5 not implemented.

## REPORT

Create only:

codex/V2/V2_R3_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
TESTS
OUTPUTS
PROVIDERS_SUPPORTED
WRAPPERS_SUPPORTED
DATA_ACCESS_RULES
SECURITY
KNOWN_LIMITATIONS
REAL_VALIDATION_COMMAND
NEXT

Machine-oriented.
Compact.
No repeated context.
No ZIP.
No additional reports.

## REAL VALIDATION COMMAND

Recommend:

python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r3_full" --verbose

Do not execute automatically unless targeted verification requires it.

## STOP

After implementation + tests:

STOP.

Expected:

V2-R3 ready for full real validation.
V2-R4 NOT STARTED.