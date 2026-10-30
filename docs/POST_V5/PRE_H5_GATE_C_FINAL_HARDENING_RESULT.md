# Pre-H5 Gate C — Endurecimiento técnico final

**Estado: `PRE_H5_GATE_C_FINAL_HARDENING = PASS`. `PRE_H5_BLOCKING_DEBT = 0`.** Gates A, A.1, B y B.1 siguen `PASS`. H5 = `NOT_STARTED`. Sin commit, push ni tag. Siguiente paso, tras revisión humana explícita: `H5_REAL_IST_VALIDATION_AND_CLOSURE`.

## 1. DT-04 — Resolución BL entre proyectos

**Diseño** (`adapters/vbnet_webforms_oracle/analysis/cross_project.py`, dentro de la etapa CALL_RESOLUTION existente; sin compilar ni cargar ensamblados, sin leer fuente):
```text
llamada → tipo del receptor (variable/instanciación/ruta calificada) → símbolos candidatos → proyecto propietario
        → alcanzabilidad por referencias DIRECTAS (ProjectReference / DLL = assembly_name) → evidencia de espacio de nombres
        → miembro y sobrecarga (aridad declarada) → arista resuelta o candidatos sin resolver
```
Precedencia: (1) símbolo totalmente calificado → CONFIRMED; (2) candidato único alcanzable + `Imports`/espacio de nombres → CONFIRMED; (3) único alcanzable sin evidencia de espacio de nombres → INFERRED; (4) en otro caso `UNRESOLVED_AMBIGUOUS_CALL`. Nunca se elige por mismo nombre de método, mismo basename de clase, mismo archivo ni cercanía.
Sobrecargas: se resuelven solo por aridad declarada (`ByVal/ByRef/Optional/ParamArray`, nuevo en la extracción: `members[].parameters`); empate → `UNRESOLVED_AMBIGUOUS_CALL`. Interfaces: varios implementadores → `UNRESOLVED_DYNAMIC_DISPATCH` (se registra el destino declarado); implementador único → INFERRED. Miembro declarado en tipo base → CONFIRMED sobre el tipo declarante. Tipo de un ensamblado referenciado que no está en la fuente → `EXTERNAL_ASSEMBLY_BOUNDARY` (ensamblados y símbolo conocido, sin inventar internos).
Además se revisa lo que las reglas base ya daban por confirmado: sobrecargas indistinguibles pasan a no resueltas, y un destino en un proyecto sin referencia directa se marca `INFERRED_UNREFERENCED_PROJECT` (la `confidence` histórica de la llamada se conserva por compatibilidad de flujos; el juicio entre proyectos es `cross_project.status`).

**Persistencia:** partición Evidence `cross_project_calls` (`cross_project_evidence_schema_version 1.0`): símbolo origen/destino, proyectos, base de resolución, nº de candidatos, candidatos, estado, `source_refs`. Las llamadas confirmadas continúan por el resolutor de flujos/BD existente (sin pipeline paralelo). Consumo downstream: contexto de IA (`cross_project_call`), documentación/visuales/entrega vía flujos persistidos; nada relee la fuente.

**Medición IST (una sola corrida determinista, ~12 min, scanner 1 / analyzer 1)**
| Medida | Antes (B.1) | Después |
|---|---|---|
| Llamadas confirmadas | 12 775 | **19 487** |
| Llamadas inferidas | 0 | 460 |
| Llamadas sin resolver | 217 581 | 210 409 |
| Flujos con terminal de datos confirmado | 2 370 | **2 500** (+130) |
| Registros entre proyectos | — | 30 576: 15 275 CONFIRMED · 848+460 INFERRED · 9 129 `EXTERNAL_ASSEMBLY_BOUNDARY` · 3 704 miembro no declarado · 1 157 ambiguas · 3 dinámicas |
Bases de las nuevas resoluciones: `unique_declaring_type` 8 489, `base_declaration` 4 872, `reference_and_namespace` 1 909 (todas con base determinista persistida). No se declara éxito por el conteo: 848 destinos sin referencia directa quedan INFERRED y 1 157 ambiguas se conservan.
Ejemplo de ruta explicada de extremo a extremo (IST, vista `ucPreMantJerarquia2`): vista → evento `MyBase.Load` → manejador `Page_Load` → `PreGesJerarquia.txtraerSupervisores` (BL) → `sysPreGesJerarquia.traerSupervisores` (datos) → operación de datos → `PPRE_GES_JERARQUIA.TRAER_SUPERVISORES`. Rutas no probables permanecen «no resuelto» (`UNRESOLVED`).

## 2. DT-07 — Segunda plantilla humana
`templates/human/executive` (solución → proyecto → capacidades → impacto en datos → no resuelto → capítulos mínimos → apéndice). Prueba: mismo modelo → `explanations.json`, `validation_report.json`, `wireframe_models.json` y `AI_INTERPRETATION_MANIFEST.json` **byte-idénticos** entre `human/default` y `human/executive` (en fixture e IST); orden de secciones distinto; 0 llamadas a proveedor; sin lecturas de fuente. Endurecimiento del contrato: `unresolved` pasa a sección obligatoria y `flow`/`actions` a partes de capítulo obligatorias (una plantilla que las omita se rechaza).

## 3. UX-03 — CLI de consumers
**Decisión B: capacidad futura no bloqueante (`FUTURE_CAPABILITY`).** La API de consumers existe y está probada; no hay CLI pública. H5 (validación IST + cierre) usa `analyze/full/docs/visuals/deliver/interpret` y el prototipo conductual, ninguno depende de consumers (prueba AST).

## 4. DT-08 — Deuda de producto seleccionada (cerrada)
* `behavior/render.py`: precedencia de operadores en la portada (`+`/`or`) fallaba (TypeError) con baselines sin huella portable → corregido.
* Contrato de plantillas: ocultar UNRESOLVED ya no es posible por configuración.
* `ANALYZER_VERSION` 3 → 4 (la extracción añade parámetros y la resolución cambia el Core): baselines anteriores requieren re-análisis explícito (`ANALYZER_VERSION_UNSUPPORTED`), nunca se reinterpretan.
* README de plantillas actualizado (sin `--source`).

## 5. Barrido de dependencias/excepciones
Resolutor nuevo sin I/O, sin `except` amplios, sin rutas absolutas ni acoplamiento a proveedores (prueba AST); grafo de `behavior/` acíclico (B.1); sin lecturas de fuente downstream (IST: 0 aperturas, scanner 0, analyzer 0, proveedor 0; conductual, conductual `executive`, `docs`, `visuals`, `deliver`).

## 6. Pruebas
* `tests/test_post_v5_gate_c_final_hardening.py` — 22 pruebas dirigidas (tipo/método entre proyectos, `Imports`, totalmente calificado, sobrecargas por aridad y empate, mismo nombre de clase en proyectos, interfaces, frontera externa, proyecto no referenciado, ruta hasta procedimiento almacenado, determinismo, fuente removida, segunda plantilla, UX-03).
* Suite completa única sobre el árbol final: `python -X utf8 -m unittest discover -s tests` → **3 454 pruebas, 0 fallos, 0 errores, 132 omitidos (históricos), exit 0, 743.2 s**.

## 7. Clasificación final de deuda
| Ítem | Clase |
|---|---|
| ≈2 570 activos con ruta relativa dependiente del contexto de ejecución | ACCEPTED_LIMITATION |
| `scan_summary.root` / `source_repository` físicos | HISTORICAL_COMPATIBILITY |
| Causa mecánica del paquete H4 de uso | ACCEPTED_LIMITATION (`UNRESOLVED_HISTORICAL_PARITY`) |
| CLI de consumers | FUTURE_CAPABILITY |
| Resolución por tipos de campo/propiedad/retorno, genéricos y tipos de argumento en sobrecargas | FUTURE_CAPABILITY |
| Llamadas `EXTERNAL_ASSEMBLY_BOUNDARY` (9 129) y miembros heredados de BCL (3 704) | ACCEPTED_LIMITATION |
| Limpieza cosmética/módulos grandes | VISUAL_POLISH_ONLY |
| **BLOCKING_BEFORE_H5** | **0** |
