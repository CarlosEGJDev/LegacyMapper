# Remediación R1 de la aceptación del propietario — interpretación de IA de sistema completo

Documento de ronda (histórico). Estado vigente: `PROJECT_STATE.json`.

```text
H5 = CLOSED    POST_V5 = CLOSED    V6 = NOT_STARTED
OWNER_STANDALONE_ACCEPTANCE = READY_FOR_RETRY   (ACC-01 corregido en el repositorio; la aceptación real aún no se repitió)
real provider calls = 0     análisis IST nuevos = 0     commit / push / tag = NO
```

## Causa raíz de ACC-01

El producto solo tenía IA conductual por proyecto (`behavior/ai.py`) e `interpret` con selección acotada de flujos. No existía
orquestación de sistema completo: ni jerarquía sistema → solución → proyecto → vista / flujo / datos, ni contrato de cobertura por
proyecto, ni identidad estable de solicitud, ni persistencia por intercambio, ni reanudación sin repetir llamadas, ni parada limpia por cuota.

## Capacidad implementada

Paquete nuevo `legacy_documenter/system/` (solo biblioteca estándar; no abre código fuente):

| Módulo | Responsabilidad |
| --- | --- |
| `inventory.py` | Inventario completo leído solo de las particiones de Evidence del baseline, con verificación de hashes contra `EVIDENCE_MANIFEST.json`. Pertenencia proyecto↔solución por ruta relativa al directorio de la solución (en el baseline real `project_refs` no coincide con los ids de proyecto) |
| `context.py` | Selección de hechos acotada y determinista por solicitud; lo omitido se declara como hecho «no resuelto», nunca en silencio |
| `planner.py` | Plan jerárquico, identidad estable y evaluación de cobertura (`assess`, función pura compartida con las proyecciones) |
| `orchestrator.py` | Ejecución, reintentos acotados, parada limpia, checkpoint por grupo de solución, métricas |
| `store.py` | Persistencia atómica de cada respuesta aceptada y registro de todos los intentos |
| `models.py` | Esquemas semánticos, vocabulario de verdad y validación determinista de afirmaciones |
| `machine.py`, `human.py`, `product.py` | Proyección de máquina (`ai/`, `internal/`), humana (HTML + `IST_Complete.pdf`) y validación del producto |
| `stub_provider.py`, `preflight.py` | Proveedor offline sintético (ensayo sin cuota) y verificación de cuenta |

Jerarquía y volumen: por proyecto resoluble `PROJECT` (+ `VIEW` en lotes de 20 vistas, máx. 6 lotes, + `DATA`); por solución `FLOW` y
`SOLUTION`; un `SYSTEM`. Nunca por archivo fuente ni con el corpus completo en una solicitud.

## Contrato CLI

```text
interpret-system <baseline> --state-dir <dir> [--provider COPILOT|STUB] [--model M] --allow-ai-interpretation
                 [--resume] [--expect-account A] [--max-requests N] [--max-retries N] [--max-consecutive-failures N]
                 [--verify-evidence hash|fast] [--knowledge-output <dir>]
project-system   <baseline> --state-dir <dir> --output <dir> [--verify-evidence hash|fast]
```

Salida 0 completo · 1 parcial/interrumpido/errores controlados · 2 uso (falta consentimiento) · 4 rechazado (baseline inválido, cuenta distinta,
SDK ausente). El proveedor real exige `--allow-ai-interpretation`; antes de cualquier solicitud se informa la identidad autenticada
(sin secretos) y `--expect-account` rechaza una cuenta distinta sin cambiarla. No hay nombres de usuario fijos en el código.

## Esquemas semánticos

`SystemInterpretation`, `SolutionInterpretation`, `ProjectInterpretation`, `ViewInterpretation`, `CrossProjectFlowInterpretation`,
`DataInteractionInterpretation` (secciones de afirmaciones `{text, status, refs, subject}`) y `FullSystemCoverageManifest`
(`FULL_SYSTEM_COVERAGE.json`: por proyecto id, identidad estable, estado, aplicabilidad de documentación humana, ids de solicitudes y
artefactos semánticos, motivo). Estados de proyecto: `HUMAN_AND_MACHINE_DOCUMENTED`, `MACHINE_ONLY_DOCUMENTED`,
`UNRESOLVED_NO_SOLUTION`, `CONTROLLED_ERROR` (y `PENDING_INTERPRETATION` solo en una corrida interrumpida). Nombres duplicados siguen
distinguibles («variante n» en lo humano; ruta e id en `ai/`).

## Contrato de reanudación

Identidad = hash de: esquema, versión de prompt, tipo, entidad, hechos exactos (con sus ids de evidencia), hashes semánticos de
dependencias y política proveedor/modelo; nunca fechas ni rutas de máquina. Respuesta aceptada con la misma identidad → 0 llamadas y se
reproduce. Cuota agotada, proveedor no disponible, presupuesto o fallos consecutivos → parada limpia con manifiesto válido y pendientes
informados; nada se omite en silencio. Un error controlado se reintenta al reanudar. Si cambia la evidencia de un proyecto, solo se
vuelve a pedir lo afectado (probado).

## Contrato de verdad

Estados humanos únicamente Confirmado / Inferido / No resuelto. Se rechazan afirmaciones con obsolescencia, identificadores de
evidencia, rutas/archivos, números de línea o diagnósticos de proveedor, referencias inexistentes, sin evidencia, o respaldadas solo por
nombres (inferencia de negocio por nombre). Una afirmación «Confirmado» sin hecho confirmado se degrada a «Inferido». El producto
humano se valida: enlaces rotos, activos, JSON, ids colgantes, fugas, vocabulario y omisiones silenciosas.

## Evidencia de pruebas

* Dirigidas: `tests/test_owner_acc01_full_system_ai.py` — 36 pruebas con proveedores stub/scripted (0 llamadas reales): inventario
  completo, planificación jerárquica, identidad estable e independiente de la máquina, integridad de baseline, cobertura, duplicados,
  no-UI, persistencia, reanudación tras cuota, replay completo con 0 llamadas y misma semántica, presupuesto, evidencia cambiada,
  fallo controlado, proveedor no disponible, excepción repetida, texto de cuota, contrato de verdad, proyección, referencias de máquina,
  determinismo sin proveedor, proyección parcial, 0 lecturas de código fuente (gancho de auditoría + escáner/extractor bloqueados) y CLI.
* Hallazgo corregido durante la ronda: en el baseline real todos los proyectos salían «sin solución» (pertenencia por id); corregido por
  ruta y blindado con un fixture que replica esa forma.
* Escala (stub, sin proveedor, baseline de aceptación de solo lectura, estado/salida en carpeta temporal): 91 soluciones / 228 proyectos →
  184 documentados, 9 solo-máquina, 35 sin solución resoluble, 0 errores; 597 solicitudes planificadas (PROJECT 184, VIEW 135, DATA 120,
  FLOW 72, SOLUTION 85, SYSTEM 1); 602 páginas HTML, PDF válido, 0 defectos de validación; 2 min 8 s.
* Perfil `devtest`: el módulo pertenece a AI_KNOWLEDGE y PACKAGING; mapa de rutas actualizado. Opciones de CLI clasificadas en
  `fingerprints.CLI_OPTION_CLASSES`; pin de módulos de producción 335 → 348 y snapshot de inventario regenerado.

## Suite completa

```text
python -X utf8 -m unittest discover -s tests   (sin LEGACYMAPPER_REAL_IST_BASELINE)
Ran 3611 tests in 906,4 s — OK (skipped=135): 0 fallos, 0 errores
```

Las corridas previas detectaron y se corrigieron: opciones de CLI sin clasificar en `fingerprints.CLI_OPTION_CLASSES`, el pin de módulos
de producción y el snapshot de inventario (nuevos módulos). La corrida definitiva se hizo con el código final; después solo cambiaron
`PROJECT_STATE.json` (bloque `owner_acceptance_remediation_r1`, `round_status`) y este documento.

## Wheel candidata

Construida desde el árbol de trabajo (no hay commit: el prompt prohíbe commit/push/tag), por lo tanto **sin SHA de commit y no apta
como wheel de aceptación**: `legacymapper-5.9.0-py3-none-any.whl`, 946 254 bytes, SHA-256
`54180991e237b009bd2ef70e2db012742d8135ffe398e8c78fb724a436bde98d` (se instaló en un venv aparte; `interpret-system --help` funciona
desde fuera del repositorio). La wheel oficial debe construirse desde el commit limpio que el propietario autorice. La evidencia previa
de aceptación (`C:\LegacyMapperAcceptance\output\*`, wheel `84607b0d…`) no se tocó.

## Pasos restantes de la aceptación

1. El propietario revisa este informe y autoriza el checkpoint de Git; se construye la wheel desde ese SHA exacto.
2. Instalar la wheel en un runtime de aceptación limpio y reutilizar `C:\LegacyMapperAcceptance\output\baseline` (esquemas 1.0 / 1.1 / 1.0
   compatibles; el hash de las particiones leídas se verifica al empezar; no se reanaliza).
3. Confirmar la cuenta de Copilot (el propietario indicó `CarlosEGJDev`): `interpret-system … --expect-account CarlosEGJDev`.
4. Paso 6: interpretación completa (≈600 solicitudes; reanudable), prueba de reanudación/replay, `project-system`, validación y revisión manual.
5. Un ensayo previo y gratuito: `--provider STUB` sobre el mismo baseline, para comprobar el producto antes de gastar cuota.

## Deuda restante

Sin deuda bloqueante de remediación. Observaciones: la calidad del texto con IA real no se pudo evaluar sin consumir cuota (el stub solo
cita hechos); las vistas por encima de 120 por proyecto se declaran como no interpretadas por límite de contexto; los 35 proyectos sin solución
resoluble se listan pero no se interpretan.
