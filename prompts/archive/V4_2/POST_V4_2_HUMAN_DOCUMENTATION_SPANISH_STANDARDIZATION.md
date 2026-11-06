# LegacyMapper — Post-V4.2 Human Documentation Spanish Standardization

## MODE

POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION

## MODEL

Claude Opus 4.6

## AUTHORITY

LegacyMapper V4.2 and the approved Post-V4.2 maintenance/documentation block
are formally closed and versioned.

This task is a documentation-only standardization round.

It does NOT reopen V4.2.

It does NOT implement V5.

It does NOT modify production behavior.

It does NOT redesign contracts.

---

# 1. NEW PERMANENT DOCUMENTATION RULE

From this point forward:

ALL DOCUMENTATION INTENDED PRIMARILY FOR HUMAN READING MUST BE WRITTEN IN SPANISH.

This includes, at minimum:

- User manuals
- Technical manuals
- Glossaries
- Architecture documents intended for human review
- Roadmaps intended for human review
- Operational guides
- Recovery guides
- Human-facing review/result documents
- Human-facing governance explanations
- Training/onboarding documents

English remains allowed and must NOT be translated when it is part of:

- source-code identifiers;
- class names;
- method/function names;
- enum names;
- contract names;
- CLI commands/options;
- environment variable names;
- file/directory names;
- JSON field names;
- Git commands;
- technology/product names;
- official protocol/API names;
- exact error messages;
- literal status values used as machine-readable contracts;
- exact quotations from source code or existing machine contracts.

Examples that must remain unchanged:

`RunResult`
`StageStatus`
`LegacyMapperPluginKnowledge`
`READY`
`NOT_IMPLEMENTED`
`V5_DESIGN_PENDING`
`python main.py readiness`
`--allow-ai-interpretation`
`ProviderRegistry`
`ARCHITECTURE_EVIDENCE.json`

The surrounding explanation must be Spanish.

---

# 2. PRIMARY OBJECTIVE

Translate and standardize the existing current human-facing LegacyMapper
documentation into Spanish while preserving:

- exact technical meaning;
- exact current behavior;
- exact file paths;
- exact contract names;
- exact statuses;
- exact commands;
- exact identifiers;
- exact hashes;
- exact Git commit SHAs;
- exact test counts;
- exact version boundaries;
- exact historical facts.

This is NOT a rewrite from memory.

This is a faithful language conversion of the already-approved content.

---

# 3. MANDATORY DOCUMENTS TO TRANSLATE

Update these current documents:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

These three are mandatory.

Do not change their filenames.

The content must become Spanish.

---

# 4. OPTIONAL HUMAN-FACING DOCUMENTS

Inspect whether these current documents are primarily intended for human use
and still contain substantial English explanatory prose:

docs/PROJECT_RECOVERY.md

docs/GENERATED_ARTIFACT_POLICY.md

PROJECT_STATE.json must NOT be translated.

AGENTS.md and CLAUDE.md must NOT be translated in this task unless the
repository rules explicitly require human-language localization.

Prompts must NOT be translated retroactively.

Historical result documents must NOT be mass-translated.

Historical closure/result documents remain historical evidence.

Only translate current living documentation that a human is expected to use
operationally going forward.

If there is uncertainty whether a document is historical evidence or current
living documentation:

do not modify it.

Report it instead.

---

# 5. TRANSLATION QUALITY RULES

Do NOT perform a literal word-for-word machine-style translation.

Produce technically natural Spanish.

Preferred style:

- clear;
- precise;
- neutral;
- professional;
- concise where possible;
- suitable for software engineers.

Avoid awkward translations of established technical concepts.

Examples:

Use:
"flujo de ejecución"

rather than unnatural alternatives.

Use:
"punto de entrada"

for entry point in explanatory prose.

Use:
"dependencia"

for dependency.

Use:
"evidencia"

for evidence.

Use:
"conocimiento canónico"

for canonical knowledge.

Use:
"frontera no resuelta"

for unresolved boundary.

Use:
"proveedor de IA"

for AI provider.

Use:
"modelo"

for model where context is clear.

Use:
"repositorio"

for repository.

Use:
"artefacto"

for artifact.

Use:
"manifiesto"

for manifest.

Do not translate technical identifiers inside code formatting.

---

# 6. PRESERVE STRUCTURE

Preserve:

- section hierarchy;
- tables;
- code blocks;
- commands;
- diagrams;
- paths;
- references;
- cross-links;
- headings numbering where present;
- file maps;
- module maps;
- debt tables;
- risk tables;
- contract tables.

You may translate human-readable headings.

Example:

`## Repository Map`

may become:

`## Mapa del repositorio`

but:

`legacy_documenter/cli/full_pipeline.py`

must remain unchanged.

---

# 7. USER MANUAL REQUIREMENTS

The Spanish User Manual must remain complete and must still explain:

- purpose;
- supported technology scope;
- installation/prerequisites;
- CLI usage;
- `analyze`;
- `full`;
- `readiness`;
- optional AI interpretation;
- output structure;
- exit codes;
- rerun/recovery behavior;
- generated-artifact policy;
- approval boundary;
- troubleshooting;
- V5 boundary.

Do not remove detail merely to shorten the document.

---

# 8. TECHNICAL MANUAL REQUIREMENTS

The Spanish Technical Manual must remain the primary:

- developer handover;
- maintenance guide;
- technical audit map.

It must preserve:

- repository map;
- package/module inventory;
- significant file map;
- main classes/functions;
- dependencies;
- execution architecture;
- pipeline stages;
- scanner/extractor/analysis architecture;
- documentation architecture;
- AI architecture;
- knowledge architecture;
- contracts/data models;
- test architecture;
- tooling;
- continuity/handover;
- generated-artifact policy;
- known debt;
- maintainability inventory;
- risk areas;
- V5 handover.

Do not reduce it to a summary.

---

# 9. GLOSSARY REQUIREMENTS

Translate the explanatory definitions to Spanish.

Preserve technical terms/identifiers where appropriate.

Preferred format:

**RunResult** — ...

**StageStatus** — ...

**Conocimiento canónico (`CanonicalKnowledge`)** — ...

If a term is primarily an implementation identifier, keep its official name
and explain it in Spanish.

Do not invent Spanish aliases that could confuse developers.

---

# 10. CURRENT STATE FACTS TO PRESERVE

The documents must continue to state the current repository facts accurately.

At minimum preserve:

V4_CLOSED=true

V4_1_CLOSED=true

V4_2_CLOSED=true

POST_V4_2_MAINTENANCE=FORMALLY_VERSIONED

TESTS=1810

TEST_FAILURES=0

TEST_ERRORS=0

EXPECTED_FRESH_CLONE_SKIPS=132

ALL_SKIPS_EXPLAINED=true

READINESS=READY

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

NEXT=V5_DESIGN_PENDING

Historical V4.2 closure commit:

af7e2099039e791c5a14ff94bf5ad348e8dbb4db

Current Post-V4.2 integration commit:

2cadd15ad63749c81fb9c350504f56abd4c36e4d

Do not alter these values.

---

# 11. DEBT / LIMITATIONS TO PRESERVE

Do not accidentally erase or soften current debt/limitations.

Preserve, where documented:

- F05 deferred-by-determinism-contract;
- F06 preserved observation;
- F07 preserved observation;
- WEB_ENTRY_POINTS scale debt;
- PROJECT_DEPENDENCIES scale debt;
- technical_documentation_renderer.py maintainability debt;
- readiness hardening if ARCHITECTURE_EVIDENCE.json is missing/corrupt;
- AI-01: GeminiProvider exists but ProviderRegistry does not expose it;
- approval surface implementation NOT_IMPLEMENTED;
- Plugin runtime NOT_IMPLEMENTED;
- V5 technology/provider/model agnosticism NOT IMPLEMENTED yet.

---

# 12. DOCUMENTATION LANGUAGE RULE RECORD

Add a short explicit section to the appropriate current human-facing
documentation policy stating:

"Idioma de la documentación para humanos"

Rule:

All new or maintained documentation intended primarily for human readers
must be written in Spanish.

Technical identifiers, code, commands, machine-readable statuses, contract
names, paths, protocol names and official technology/product names remain in
their original form.

Prefer updating:

docs/GENERATED_ARTIFACT_POLICY.md

only if it is already the natural policy location.

If that document is not semantically appropriate, use:

docs/PROJECT_RECOVERY.md

or create a narrowly scoped:

docs/HUMAN_DOCUMENTATION_LANGUAGE_POLICY.md

Do not create a new policy file unless necessary.

---

# 13. PRODUCTION / TEST BOUNDARY

Expected:

PRODUCTION_CODE_CHANGED=false

TESTS_CHANGED=false

Do NOT modify:

legacy_documenter/**

tests/**

output/v4_2_r8/V4_2_FINAL_BASELINE.json

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

Do not change runtime behavior.

---

# 14. VALIDATION

Perform documentation consistency validation only.

Check:

- no code identifier was accidentally translated;
- no CLI command was altered;
- no path was altered;
- no hash/commit SHA was altered;
- no status enum/value was translated;
- no JSON field was translated;
- no historical count changed;
- no V5 capability is described as already implemented;
- no Plugin Runtime is described as implemented;
- no approval surface is described as implemented.

A full test-suite run is NOT required because production/tests are unchanged.

You may run lightweight validation if helpful.

Do not access real IST.

Do not call any real AI provider.

---

# 15. RESULT DOCUMENT

Create:

docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION_RESULT.md

Write this result document itself in Spanish.

Required sections:

## ESTADO

## OBJETIVO

## REGLA_DE_IDIOMA

## DOCUMENTOS_ACTUALIZADOS

## DOCUMENTOS_NO_MODIFICADOS

## IDENTIFICADORES_TECNICOS_PRESERVADOS

## CONSISTENCIA_TECNICA

## DATOS_HISTORICOS_PRESERVADOS

## DEUDA_Y_LIMITACIONES_PRESERVADAS

## CAMBIOS_DE_POLITICA_DOCUMENTAL

## CODIGO_DE_PRODUCCION_MODIFICADO

## TESTS_MODIFICADOS

## PROVEEDOR_IA_REAL

## IST_REAL_ACCEDIDO

## ESTADO_V4_2

## ESTADO_V5

## ESTADO_GIT

## DECISION

## SIGUIENTE

Expected:

ESTADO=COMPLETO

CODIGO_DE_PRODUCCION_MODIFICADO=false

TESTS_MODIFICADOS=false

PROVEEDOR_IA_REAL=0

IST_REAL_ACCEDIDO=false

V4_2_REABIERTO=false

V5_IMPLEMENTADO=false

DECISION=DOCUMENTACION_HUMANA_EN_ESPAÑOL_LISTA_PARA_REVISION_DEL_LIDER_TECNICO

SIGUIENTE=REVISION_HUMANA_DOCUMENTACION_ESPAÑOL

---

# 16. GIT

Do NOT commit.

Do NOT push.

Do NOT modify PROJECT_STATE.json yet.

The Technical Lead must review the Spanish documentation before versioning.

---

# 17. STOP CONDITIONS

STOP if:

- translation changes technical meaning;
- an identifier/contract/status cannot be safely distinguished from prose;
- a current manual contradicts current repository state;
- translation would require changing production/test behavior;
- historical evidence would need rewriting;
- a document's status as living vs historical is unclear;
- any secret/security issue is found.

Report the issue instead of guessing.

---

# 18. END

Stop after producing the translated current documentation and result.

Do NOT start V5.

Do NOT commit.

Do NOT push.