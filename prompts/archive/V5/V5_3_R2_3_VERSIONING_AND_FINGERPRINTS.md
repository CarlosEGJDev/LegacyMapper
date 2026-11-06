# LegacyMapper V5.3 — R2.3 Versionado y fingerprints

## 1. Objetivo

Implementar únicamente el bloque de versionado y fingerprints definido en V5.3 R1.

Esta ronda debe dejar resuelto:

- `ANALYZER_VERSION`;
- `ANALYZER_CODE_FINGERPRINT`;
- `CONFIG_FINGERPRINT`;
- `TEMPLATE_PROFILE_FINGERPRINT`;
- registro de versiones de renderers existentes;
- hash semántico de archivos analizados;
- guardianes de tests para evitar reutilización insegura futura.

NO implementar todavía File State ni caché persistida.

## 2. Fuentes obligatorias

Leer antes de modificar:

- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`
- `docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

## 3. Corrección documental previa

En:

`docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`

aparece una frase desactualizada indicando que el cierre Git de V5.2 sigue `PENDING_GIT_APPROVAL`.

Eso es incorrecto.

V5.2 ya fue:

- committeada;
- etiquetada con `v5.2`;
- publicada en `origin/main`;
- publicada como tag remoto.

Corregir únicamente esa frase en el informe R2.2.1.

No tocar otros documentos históricos.

## 4. Alcance permitido

Modificar únicamente lo necesario para:

1. crear un módulo runtime de versiones;
2. calcular fingerprints deterministas;
3. añadir helpers de hash semántico;
4. exponer esos valores al runtime futuro;
5. añadir tests guardianes;
6. documentar qué cambios invalidarán caché futura.

No crear todavía la caché que los consumirá.

## 5. Contrato de versionado

### 5.1 ANALYZER_VERSION

Crear una constante explícita:

`ANALYZER_VERSION`

Debe cubrir cambios que puedan alterar:

- extracción;
- scanner/clasificación;
- normalización de namespaces;
- partial classes;
- resolvers;
- evidencia derivada de análisis.

Usar una representación simple y estable, preferentemente entero.

No usar Git commit como versión.

### 5.2 EVIDENCE_SCHEMA_VERSION

NO duplicar.

Reutilizar la constante existente:

`legacy_documenter.evidence.entities.EVIDENCE_SCHEMA_VERSION`

No crear otra equivalente.

### 5.3 RENDERER_VERSIONS

Registrar las familias existentes sin romper sus contratos.

Como mínimo revisar:

- legacy markdown;
- human documentation;
- consumer projection;
- ai_context;
- hydration;
- documentation_v52.

Si una familia ya tiene `MODEL_VERSION`, `SCHEMA_VERSION` o `CONTRACT_VERSION`, reutilizarla.

Crear nueva constante solo donde realmente falta.

### 5.4 Git metadata

Puede registrarse como metadata futura, pero no debe entrar en la clave principal de invalidación.

## 6. ANALYZER_CODE_FINGERPRINT

Implementar un fingerprint SHA-256 determinista del código que gobierna el análisis.

Debe incluir, como mínimo, las fuentes relevantes de:

- `extractors/`;
- `analysis/`;
- scanner/clasificación;
- modelos usados por extracción;
- `utils/sanitizer.py`;
- `config.py`;
- funciones de extracción/normalización en `pipeline_stages.py`.

### Requisitos

- orden estable de archivos;
- rutas relativas normalizadas;
- contenido de archivo incluido;
- algoritmo documentado;
- mismo código → mismo fingerprint;
- un byte cambiado en un módulo incluido → fingerprint distinto;
- no depender de timestamps;
- no depender de Git;
- no leer docs, prompts, tests ni `PROJECT_STATE.json`.

Si los fuentes no son legibles:

- devolver un estado explícito de indisponibilidad;
- la futura caché deberá considerar eso como motivo para no reutilizar extracción.

No implementar todavía el fallback de caché; solo exponer el dato.

## 7. CONFIG_FINGERPRINT

Implementar SHA-256 sobre JSON canónico de la configuración efectiva que afecta análisis/proyección.

Debe clasificar al menos:

### Sí afecta

- `DEFAULT_EXCLUDES`;
- `--exclude`;
- `flow_max_depth`;
- idioma;
- perfiles de `documentation_v52`;
- `custom_dir`;
- `strict_templates`;
- cualquier otra opción actual que cambie análisis o salida determinista.

### No afecta al fingerprint de análisis

- `allow_ai_interpretation`;
- opciones puramente de logging;
- `--verbose`;
- rutas de salida;
- opciones de ejecución que no cambien contenido lógico.

Si conviene separar:

- `analysis_config_fingerprint`;
- `projection_config_fingerprint`;

puede hacerse, pero justificarlo.

No mezclar opciones sin explicar su efecto.

## 8. Guardián de opciones CLI

Crear un test que enumere las opciones actuales de CLI relevantes y exija que cada una esté clasificada explícitamente como:

- analysis-affecting;
- projection-affecting;
- runtime-only;
- ai-only;
- output-location-only.

El objetivo es evitar que una opción nueva se agregue en el futuro sin decidir si debe invalidar caché.

No duplicar el parser.

La fuente de verdad debe ser el parser/configuración real.

## 9. TEMPLATE_PROFILE_FINGERPRINT

Implementar SHA-256 determinista que cubra el contenido efectivo de:

`documentation_v52/defaults/`

Incluyendo, según corresponda:

- templates;
- profiles;
- i18n;
- noise;
- idioma;
- perfiles activos;
- `custom_dir` si existe.

### Requisitos

- mismo contenido efectivo → mismo fingerprint;
- cambio de template → cambia fingerprint;
- cambio de profile → cambia fingerprint;
- cambio de idioma → cambia fingerprint;
- orden de lectura no afecta;
- rutas relativas normalizadas;
- no depende de mtime.

No modificar el contenido de defaults.

## 10. Hash semántico de archivos

Implementar helper para tipos de texto analizados.

Contrato:

### Hash crudo

NO cambiar:

`SourceArtifact.sha256`

Sigue siendo SHA-256 de bytes reales.

### Hash semántico

Para archivos de texto analizados:

- `\r\n` → `\n`;
- `\r` → `\n`;
- BOM preservado;
- espacios preservados;
- encoding tratado de forma determinista.

Debe demostrar:

- CRLF y LF equivalentes → mismo hash semántico;
- BOM distinto → hash semántico distinto;
- espacios distintos → hash semántico distinto;
- cambio real de contenido → hash distinto.

Para binarios o tipos no analizados:

- no normalizar;
- devolver `None` o usar hash crudo según contrato explícito.

No sustituir el hash crudo existente.

## 11. API mínima esperada

Preferir una API pequeña y clara, por ejemplo:

```python
ANALYZER_VERSION
analyzer_code_fingerprint()
analysis_config_fingerprint(...)
projection_config_fingerprint(...)
template_profile_fingerprint(...)
semantic_content_sha256(...)
renderer_versions()
```

Los nombres exactos pueden variar si hay una razón clara.

No crear una jerarquía compleja.

## 12. Runtime independence

Los nuevos módulos NO pueden depender de:

- docs;
- prompts;
- tests;
- `PROJECT_STATE.json`;
- gobernanza;
- Copilot;
- IA.

Biblioteca estándar preferida.

No introducir nueva dependencia externa.

## 13. Tests obligatorios — versiones

Crear tests para:

1. `ANALYZER_VERSION` existe y tiene tipo estable;
2. `EVIDENCE_SCHEMA_VERSION` reutilizado, no duplicado;
3. familias de renderer correctamente registradas;
4. ningún cambio de contrato de salida por esta ronda;
5. runtime independence.

## 14. Tests obligatorios — code fingerprint

Cubrir:

1. mismo árbol de código → mismo fingerprint;
2. orden de enumeración distinto → mismo fingerprint;
3. cambio en extractor incluido → fingerprint distinto;
4. cambio en módulo de análisis incluido → distinto;
5. cambio en archivo fuera de alcance (docs/prompts/tests) → no afecta;
6. timestamps distintos → no afectan;
7. fuente ilegible/ausente → estado explícito y seguro;
8. rutas normalizadas;
9. determinismo entre dos ejecuciones.

## 15. Tests obligatorios — config fingerprint

Cubrir:

1. `DEFAULT_EXCLUDES` cambia → fingerprint cambia;
2. `--exclude` mismo conjunto distinto orden → mismo fingerprint;
3. `flow_max_depth` cambia → cambia;
4. idioma cambia → projection fingerprint cambia;
5. perfil cambia → cambia;
6. `custom_dir` cambia → cambia;
7. `allow_ai_interpretation` no invalida análisis;
8. `verbose` no cambia;
9. output path no cambia;
10. clasificación completa de opciones CLI.

## 16. Tests obligatorios — template/profile

Cubrir:

1. mismos archivos distinto orden → mismo fingerprint;
2. template cambia → distinto;
3. profile cambia → distinto;
4. i18n cambia → distinto;
5. noise cambia → distinto;
6. custom_dir se incorpora;
7. archivo agregado/eliminado → distinto;
8. mtime sin cambio de contenido → mismo fingerprint.

## 17. Tests obligatorios — hash semántico

Cubrir:

1. CRLF vs LF → mismo;
2. CR vs LF → mismo;
3. BOM vs sin BOM → distinto;
4. espacios finales distintos → distinto;
5. contenido distinto → distinto;
6. archivo vacío;
7. tipo no analizado;
8. determinismo;
9. hash crudo sigue distinto donde corresponde;
10. no modifica `SourceArtifact.sha256`.

## 18. Guardián ANALYZER_VERSION

Implementar un test que ayude a detectar:

“cambió código relevante del analizador pero nadie subió `ANALYZER_VERSION`”.

Puede usar un valor esperado del fingerprint o un mecanismo equivalente.

Requisitos:

- no poner ese valor esperado en runtime;
- debe vivir en tests;
- mensaje de fallo claro;
- actualizarlo requiere intención explícita.

No crear deuda circular donde el test se autoactualice.

## 19. Integración

Esta ronda puede exponer los nuevos valores desde módulos runtime, pero NO debe:

- añadir `_cache_v53/`;
- persistir manifest de caché;
- cambiar flujo de ejecución;
- decidir full vs incremental;
- evitar stages;
- reutilizar extracción.

El comportamiento observable del pipeline debe seguir igual que R2.2.1.

## 20. Suite

Ejecutar:

- tests dirigidos nuevos;
- tests de CLI/config;
- tests de documentation_v52 si se toca configuración;
- tests de Evidence Core relacionados con schema/hash;
- test de runtime independence;
- suite completa:
  `python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

## 21. Validación IST

No hace falta repetir dos corridas completas si la ronda no cambia ejecución.

Ejecutar como mínimo una validación controlada que demuestre:

- fingerprints se pueden calcular sobre IST;
- son deterministas;
- no cambian outputs;
- hash semántico se calcula sobre los tipos analizados;
- coste de cálculo es razonable.

Medir:

- tiempo `ANALYZER_CODE_FINGERPRINT`;
- tiempo de fingerprints de configuración/templates;
- tiempo de calcular hashes semánticos sobre IST;
- memoria si es relevante.

Si el cambio toca flujo productivo más de lo previsto, entonces ejecutar una corrida completa IST.

## 22. Deuda técnica

Clasificar:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

Revisar especialmente:

- duplicación de versiones;
- demasiadas constantes;
- fingerprint demasiado amplio;
- fingerprint demasiado estrecho;
- coste de hash semántico;
- acoplamiento con parser;
- fuentes no legibles en distribución instalada.

No corregir deuda fuera de alcance.

## 23. Git

Solo consultas.

No commit, tag ni push.

Registrar:

- archivos modificados;
- archivos nuevos;
- pendientes previos.

## 24. Entregable

Crear:

`docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md`

Debe incluir:

1. Objetivo.
2. Corrección documental realizada.
3. Archivos modificados.
4. `ANALYZER_VERSION`.
5. `ANALYZER_CODE_FINGERPRINT`.
6. `EVIDENCE_SCHEMA_VERSION`.
7. `RENDERER_VERSIONS`.
8. `CONFIG_FINGERPRINT`.
9. Clasificación de opciones CLI.
10. `TEMPLATE_PROFILE_FINGERPRINT`.
11. Hash semántico.
12. API final.
13. Tests dirigidos.
14. Guardián de versión.
15. Suite completa.
16. Validación IST.
17. Costes medidos.
18. Deuda técnica.
19. Riesgos.
20. Fuera de alcance confirmado.
21. Estado Git.
22. Estado final.

## 25. Estados finales permitidos

Si todo cumple:

`V5_3_R2_3_READY_FOR_REVIEW`

Si hay fingerprint no determinista, clasificación incompleta, tests fallidos o riesgo de invalidación insegura:

`V5_3_R2_3_BLOCKED`

No usar otro estado.

## 26. Restricciones finales

No:

- iniciar R2.4;
- crear File State;
- crear `_cache_v53/`;
- crear `CACHE_MANIFEST.json`;
- implementar extraction cache;
- cambiar Evidence Core;
- cambiar IDs;
- cambiar manifests existentes;
- ejecutar IA;
- commit/push.

Detenerse para revisión humana.
