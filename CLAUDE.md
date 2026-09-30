# Claude Code — LegacyMapper

Lee y respeta primero:

1. `AGENTS.md`
2. `PROJECT_STATE.json`
3. `docs/V4/V4_AI_HANDOVER.md`
4. `output/v3_final/V3_FINAL_BASELINE.json`
5. el prompt activo de `prompts/V4/`

Si el repositorio no compila mentalmente (checkout nuevo, sin memoria de sesión), ver `docs/PROJECT_RECOVERY.md`.

No asumas contexto desde conversaciones anteriores.

El repositorio es la fuente autoritativa del estado del proyecto.

No dupliques reglas ni conocimiento aquí.

## Reglas de creación de documentación

Claude NO debe crear archivos `.md` adicionales por iniciativa propia.

Solo puede crear:

1. Los `.md` explícitamente solicitados por el prompt actual.
2. El documento de resultado obligatorio de la ronda.
3. El prompt de la siguiente ronda, únicamente si el prompt actual lo autoriza.

No crear archivos separados como:

- FIX_NOTES.md
- PATCH_RESULT.md
- CORRECCION.md
- DIAGNOSTICO_EXTRA.md
- TODO_FIX.md
- WORKAROUND.md

Cualquier hallazgo adicional debe incorporarse dentro del documento de resultado de la ronda.

Si una ronda necesita corrección, no crear documentos retroactivos ni nuevas rondas por cuenta propia.
Esperar autorización explícita para crear R1A, R2A, R3A, etc.

Regla preferida:

1 ronda → 1 documento de resultado → opcionalmente 1 prompt siguiente