# LegacyMapper V5 — Clean-Room User Acceptance Environment

## Objetivo
Preparar un ambiente de uso real fuera de `C:\dev\LegacyMapper` para que el propietario pruebe V5 desde cero, aprenda los comandos reales y vea la documentación humana y el contexto para IA.

No es desarrollo. No iniciar V6.

## Release
Usar:
- tag `v5`
- commit `e831a2f84d2749b4452e06860521b3171093c7b9`

Verificar primero que `v5` apunta exactamente a ese commit.

## Root limpio
Usar:
`C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE`

Estructura:
- `app\`
- `targets\`
- `outputs\`
- `samples\`
- `logs\`
- `notes\`
- `.venv\`

## 1. Crear release desde el tag
Preferir `git archive v5` y extraerlo a `app\`.
No copiar el working tree de desarrollo.

Si se usa clone, debe ser detached sobre tag `v5`.

No usar `C:\dev\LegacyMapper` como cwd, PYTHONPATH, template source, docs source, import source o fallback runtime.

## 2. Prueba de independencia
Buscar referencias a `C:\dev\LegacyMapper` y distinguir:
- runtime dependency;
- texto histórico en docs/tests.

Durante las corridas probar que los archivos runtime salen solo de:
- `...\V5_USER_ACCEPTANCE\app`
- target elegido
- output elegido

Si hay dependencia runtime real:
`V5_CLEANROOM_BLOCKED_DEV_DEPENDENCY`.

## 3. Determinar el modelo real de ejecución
No adivinar. Inspeccionar:
- `README.md`
- `docs/V5/V5_OPERATIONS_GUIDE.md`
- `pyproject.toml`, `setup.cfg`, requirements si existen
- `main.py`
- parser/`--help`

Determinar si se ejecuta desde source, package install, editable install, etc.
No acceder a red automáticamente.

## 4. Ambiente Python aislado
Crear `.venv` dentro del clean-room.
Registrar:
- `python --version`
- `where python`
- `sys.executable`
- `sys.path`

Nada debe apuntar al venv de desarrollo.

Instalar/configurar solo según las instrucciones reales del repo.

## 5. Descubrir CLI real
Ejecutar `--help` real para:
- `analyze`
- `full`
- `readiness`
- `output-manifest`
- `review`
- `review list`
- `review prepare`
- `review decide`
- `review canonical`

Verificar si existe CLI de consumers. La auditoría dice que no existe, pero comprobarlo.

## 6. Cheat sheet
Crear:
`notes\V5_USER_COMMANDS.md`

Para cada comando:
- propósito
- sintaxis mínima
- opciones importantes
- output esperado
- exit behavior
- ejemplo copiable

Incluir `--repository-id`.
Separar modo determinista y modo con IA.
No hacer provider real todavía.

## 7. Primer test pequeño
Elegir un target pequeño y seguro.
Copiarlo a:
`targets\first_sample`

Ejecutar el análisis determinista más simple soportado.
Registrar:
- comando
- exit code
- duración
- árbol de salida
- Evidence
- documentación humana

## 8. Test Python
Si está disponible la fuente congelada autorizada, copiarla a:
`targets\python_pilot`

Ejecutar desde el clean-room con:
`--repository-id SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60`
usando la sintaxis real confirmada por `--help`.

Probar:
- adapter `python-generic`
- source sin mutación
- 0 dependencia del dev repo
- 0 provider real

## 9. Comando IST para el usuario
Preparar, no ejecutar automáticamente si es costoso.
Debe ejecutarse desde `app\`, AI OFF.
Documentar baseline esperado:
- source files 15138
- output files 47523
- output bytes 2828066791

## 10. Documentación para humanos
Ubicar físicamente:
- human-functional
- human-technical

Confirmar cómo se mapean a perfiles/path reales, probablemente:
- `general_overview`
- `developer_technical`

Crear:
`notes\WHERE_TO_READ_HUMAN_DOCS.md`

Explicar:
- dónde empezar;
- overview funcional;
- navegación técnica;
- Solution → Project → File → Component → Method;
- evidence/traceability;
- qué significa unresolved;
- qué es hecho determinista vs presentación.

## 11. Documentación/contexto para IA
Ubicar:
- AI context;
- hydrated projection;
- segmented context cuando aplique;
- proposals cuando se use Fake provider.

Crear:
`notes\WHERE_TO_READ_AI_CONTEXT.md`

Explicar:
`Evidence → AI context → provider → proposal → human review → canonical`

Aclarar:
`AI proposal != canonical knowledge`.

## 12. Demo Fake provider
Si está soportado como workflow de prueba sin modificar producto:
- networkless
- real provider calls = 0
- proposal READY_FOR_REVIEW
- canonical = false

Después demostrar review CLI sobre copia controlada.
No aprobar silenciosamente en nombre del usuario.

## 13. Consumer API
Como no se espera CLI de consumers, crear ejemplo read-only:
`samples\consumer_read_example.py`

Demostrar al menos:
- READ_EVIDENCE
- READ_FLOW
- READ_AI_CONTEXT
- RENDER_HUMAN_DOC

Importar solo desde release clean-room.
Explicar Plugin Contract != Plugin Runtime.

## 14. START_HERE
Crear:
`notes\START_HERE.md`

Debe ser el manual del usuario:
1. abrir terminal;
2. activar venv;
3. confirmar tag/version;
4. ver help;
5. analizar first_sample;
6. encontrar Evidence;
7. abrir human-functional;
8. abrir human-technical;
9. inspeccionar AI context;
10. Fake provider opcional;
11. review workflow;
12. consumer example;
13. comando IST opcional;
14. borrar outputs y rerun;
15. limitaciones conocidas.

Todos los comandos deben ser copy/paste y haber sido verificados.

## 15. Limitaciones a mostrar
- `SELF_HOSTED_CIRCULAR`
- external independence no probada
- `repository_id` opt-in
- Plugin Runtime no implementado
- consumers read-only
- unresolved Python esperado por análisis estático
- scope incremental puede reportar `mode=full`

## 16. Informe final
Crear:
`notes\V5_CLEANROOM_VALIDATION.md`

Debe reportar:
- tag/commit;
- método de release;
- Python/venv;
- modelo de ejecución;
- auditoría de dependencia dev;
- CLI verificada;
- primer run;
- Python run;
- paths de docs humanas;
- paths de contexto IA;
- Fake provider/review;
- consumer example;
- source mutation;
- network/provider calls;
- blockers/observations;
- siguientes pasos manuales.

## Git
No modificar `C:\dev\LegacyMapper`.
No commit/push/tag durante esta tarea.
Solo queries/archive.

## Éxito
`V5_CLEANROOM_READY_FOR_USER_ACCEPTANCE`

Requiere:
- corre fuera de dev;
- sin dependencia runtime a archivos de desarrollo;
- CLI real documentada desde help;
- docs humanas localizadas;
- contexto IA localizado;
- run determinista exitoso;
- real provider calls = 0;
- source intacta;
- `START_HERE.md` creado.
